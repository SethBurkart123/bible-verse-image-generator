import fs from 'fs';
import path from 'path';
import readline from 'readline';
import { setTimeout } from 'timers/promises';
import chalk from 'chalk';

const headers = {
    "accept": "*/*",
    "accept-language": "en-US",
    "client-geo-region": "global",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Chromium\";v=\"129\", \"Not=A?Brand\";v=\"8\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "Referer": "https://unsplash.com/s/photos/nature?license=free&orientation=portrait",
    "Referrer-Policy": "origin-when-cross-origin"
};

const DOWNLOADED_IMAGES_FILE = 'downloaded-images.json';

function loadDownloadedImages() {
    if (fs.existsSync(DOWNLOADED_IMAGES_FILE)) {
        const data = fs.readFileSync(DOWNLOADED_IMAGES_FILE, 'utf8');
        return new Set(JSON.parse(data));
    }
    return new Set();
}

function saveDownloadedImages(downloadedImages) {
    fs.writeFileSync(DOWNLOADED_IMAGES_FILE, JSON.stringify([...downloadedImages]), 'utf8');
}

function createProgressBar(total) {
    const barLength = 30;
    let current = 0;
    let totalUnique = 0;

    const update = (value, uniqueCount) => {
        current = value;
        totalUnique = uniqueCount;
        const percentage = Math.round((current / total) * 100);
        const filledLength = Math.round((current / total) * barLength);
        const bar = '█'.repeat(filledLength) + '░'.repeat(barLength - filledLength);

        readline.cursorTo(process.stdout, 0);
        process.stdout.write(`Progress: [${bar}] ${percentage}% | ${current}/${total} images | Total unique: ${totalUnique}`);
    };

    const log = (message) => {
        readline.cursorTo(process.stdout, 0);
        readline.clearLine(process.stdout, 0);
        console.log(message);
        update(current, totalUnique);
    };

    return { update, log };
}

async function downloadImage(url, filepath, fetch, log) {
    try {
        const response = await fetch(url, { headers });
        if (response.ok) {
            const buffer = await response.arrayBuffer();
            fs.writeFileSync(filepath, Buffer.from(buffer));
            log(chalk.green(`Downloaded: ${filepath}`));
        } else {
            log(chalk.red(`Failed to download: ${url}`));
        }
    } catch (error) {
        log(chalk.red(`Error downloading ${url}: ${error.message}`));
    }
}

async function searchImages(query, numImages, fetch) {
    let allPhotos = [];
    let page = 1;

    while (allPhotos.length < numImages) {
        const url = `https://unsplash.com/napi/search/photos?query=${query}&page=${page}&per_page=${Math.min(20, numImages)}&orientation=portrait`;
        
        try {
            const response = await fetch(url, { headers });
            if (!response.ok) {
                console.error(`Failed to fetch images: ${response.status}`);
                break;
            }

            const data = await response.json();
            const photos = data.results || [];
            allPhotos = allPhotos.concat(photos);

            if (photos.length === 0 || allPhotos.length >= numImages) {
                break;
            }

            page++;
            // Rate limiting: wait for 1 second between requests
            await setTimeout(1000);
        } catch (error) {
            console.error(`Error fetching images: ${error.message}`);
            break;
        }
    }

    return allPhotos.slice(0, numImages);
}

async function downloadImages(query, numImages, fetch) {
    const images = await searchImages(query, numImages, fetch);
    let downloadedImages = loadDownloadedImages();

    if (!fs.existsSync('backgrounds')) {
        fs.mkdirSync('backgrounds');
    }

    let newDownloads = 0;
    let totalDownloads = downloadedImages.size;
    let processedImages = 0;

    const progressBar = createProgressBar(numImages);

    for (const image of images) {
        const imageUrl = image.urls.regular;
        const imageId = image.id;

        if (imageUrl.startsWith('https://plus.unsplash.com')) {
            progressBar.log(chalk.yellow(`Skipping premium image: ${imageId}`));
            processedImages++;
            progressBar.update(processedImages, totalDownloads);
            continue;
        }

        if (!downloadedImages.has(imageUrl)) {
            const filepath = path.join('backgrounds', `${imageId}.jpg`);
            await downloadImage(imageUrl, filepath, fetch, progressBar.log);
            downloadedImages.add(imageUrl);
            newDownloads++;
            totalDownloads++;
        } else {
            progressBar.log(chalk.yellow(`Skipping previously downloaded image: ${imageId}`));
        }

        processedImages++;
        progressBar.update(processedImages, totalDownloads);

        // Rate limiting: wait for 1 second between downloads
        await setTimeout(1000);
    }

    console.log('\n');  // Move to the next line after the progress bar
    saveDownloadedImages(downloadedImages);
    console.log(chalk.green(`Downloaded ${newDownloads} new images (${totalDownloads} total unique images)`));
}

function prompt(question) {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise((resolve) => {
        rl.question(question, (answer) => {
            rl.close();
            resolve(answer);
        });
    });
}

async function main() {
    const defaultSearchQuery = "nature";
    const defaultNumImages = 10;

    console.log(chalk.cyan('Welcome to the Image Downloader!'));
    const searchQuery = await prompt(chalk.magenta(`Enter search query [default: ${defaultSearchQuery}]: `)) || defaultSearchQuery;
    let numImagesToDownload;

    while (true) {
        const numImagesInput = await prompt(chalk.magenta(`Enter number of images to download [default: ${defaultNumImages}]: `)) || defaultNumImages;
        numImagesToDownload = parseInt(numImagesInput);

        if (numImagesToDownload > 0) {
            break;
        } else {
            console.log(chalk.red("Please enter a positive number."));
        }
    }

    console.log(chalk.cyan(`Downloading ${numImagesToDownload} images for query: ${searchQuery}`));
    await downloadImages(searchQuery, numImagesToDownload, fetch);
}

main().catch(console.error);