import sqlite3
import json
import logging
from fuzzywuzzy import process
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from collections import OrderedDict
import re

# Set up rich console and logging
console = Console()
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, console=console)]
)

# Function to retrieve a specific verse from the database
def get_verse_by_reference(book_name, chapter, verse):
    # Path to the SQLite file
    db_path = "./bible/NLT2015.SQLite3"
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    
    # Query to get all book names
    all_books_query = "SELECT long_name FROM books_all;"
    all_books = [row[0] for row in conn.execute(all_books_query).fetchall()]
    
    # Perform fuzzy matching
    best_match, score = process.extractOne(book_name, all_books)
    logging.debug(f"Fuzzy match for '{book_name}': '{best_match}' (score: {score})")
    
    if score < 60:  # You can adjust this threshold
        conn.close()
        logging.warning(f"No close match found for book: {book_name}")
        return None
    
    # Use the best match for the query
    book_query = """
    SELECT book_number FROM books_all WHERE long_name = ?;
    """
    
    # Get the book_number for the matched book name
    book_number_result = conn.execute(book_query, (best_match,)).fetchone()
    
    if not book_number_result:
        conn.close()
        logging.warning(f"Book not found: {best_match}")
        return None  # Book not found
    
    book_number = book_number_result[0]
    logging.debug(f"Book number for {best_match}: {book_number}")
    
    # Query to get the verse text based on book_number, chapter, and verse
    verse_query = """
    SELECT text FROM verses WHERE book_number = ? AND chapter = ? AND verse = ?;
    """
    
    # Execute the query to get the verse
    verse_result = conn.execute(verse_query, (book_number, chapter, verse)).fetchone()
    
    conn.close()
    
    if verse_result:
        logging.debug(f"Verse found: {best_match} {chapter}:{verse}")
        return verse_result[0]  # Return the verse text
    else:
        logging.warning(f"Verse not found: {best_match} {chapter}:{verse}")
        return None  # Verse not found

# Updated function to clean verse text
def clean_verse_text(text):
    # Remove HTML-like tags
    text = text.replace('<pb/>', '').replace('<J>', '').replace('</J>', '')\
               .replace('<f>', '').replace('</f>', '').replace('<t>', '').replace('</t>', '')\
               .replace('<e>', '').replace('</e>', '')   
    
    # Remove numbered references in square brackets
    text = re.sub(r'\[\d+\]', '', text)
    
    # Remove any extra whitespace
    text = ' '.join(text.split())
    
    return text

# Updated function to process references, handle verse ranges, multiple verses, and filter duplicates
def process_verse_references(verse_references):
    console.print(f"[bold green]Processing {len(verse_references)} verse references[/bold green]")
    output = []
    processed_references = set()
    duplicate_count = 0
    
    # Calculate total number of verses
    total_verses = 0
    for ref in verse_references:
        reference = ref['reference']
        try:
            _, verses = reference.split(':', 1)
            total_verses += sum(len(range(int(v.split('-')[0]), int(v.split('-')[-1]) + 1)) if '-' in v else 1 
                                for v in verses.split(','))
        except ValueError:
            console.print(f"[yellow]⚠[/yellow] Invalid reference format: {reference}")
            total_verses += 1  # Assume one verse for invalid formats
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        verse_task = progress.add_task("[cyan]Processing verses...", total=total_verses)
        
        for ref in verse_references:
            reference = ref['reference']
            
            try:
                parts = reference.split()
                if len(parts) < 2:
                    raise ValueError("Invalid reference format")
                
                book = ' '.join(parts[:-1])
                chapter_verse = parts[-1]
                
                if ':' not in chapter_verse:
                    raise ValueError("Invalid chapter:verse format")
                
                chapter, verses = chapter_verse.split(':')
                chapter = int(chapter)
                
                verse_parts = verses.split(',')
                
                for part in verse_parts:
                    part = part.strip()
                    if '-' in part:
                        # Handle verse range (e.g., 5-6)
                        verse_start, verse_end = map(int, part.split('-'))
                        for verse_num in range(verse_start, verse_end + 1):
                            full_reference = f"{book} {chapter}:{verse_num}"
                            if full_reference in processed_references:
                                console.print(f"[yellow]⚠[/yellow] Duplicate found: {full_reference}")
                                duplicate_count += 1
                            else:
                                verse_text = get_verse_by_reference(book, chapter, verse_num)
                                if verse_text:
                                    clean_text = clean_verse_text(verse_text)
                                    output.append({
                                        "reference": full_reference,
                                        "text": clean_text
                                    })
                                    processed_references.add(full_reference)
                                    console.print(f"[green]✓[/green] {full_reference}")
                                else:
                                    console.print(f"[yellow]⚠[/yellow] Verse not found: {full_reference}")
                            progress.update(verse_task, advance=1)
                    else:
                        # Handle single verse
                        verse_num = int(part)
                        full_reference = f"{book} {chapter}:{verse_num}"
                        if full_reference in processed_references:
                            console.print(f"[yellow]⚠[/yellow] Duplicate found: {full_reference}")
                            duplicate_count += 1
                        else:
                            verse_text = get_verse_by_reference(book, chapter, verse_num)
                            if verse_text:
                                clean_text = clean_verse_text(verse_text)
                                output.append({
                                    "reference": full_reference,
                                    "text": clean_text
                                })
                                processed_references.add(full_reference)
                                console.print(f"[green]✓[/green] {full_reference}")
                            else:
                                console.print(f"[yellow]⚠[/yellow] Verse not found: {full_reference}")
                        progress.update(verse_task, advance=1)
            except Exception as e:
                console.print(f"[red]✗[/red] Error processing reference {reference}: {str(e)}")
                progress.update(verse_task, advance=1)
    
    console.print(f"[bold green]Processed {len(output)} unique verses successfully[/bold green]")
    console.print(f"[bold yellow]Found {duplicate_count} duplicate references[/bold yellow]")
    return output

# Function to read references from a TXT file
def read_references_from_txt(input_file):
    console.print(f"[bold blue]Reading verse references from {input_file}[/bold blue]")
    with open(input_file, 'r') as file:
        references = [line.strip() for line in file if line.strip()]
    console.print(f"[green]Read {len(references)} verse references[/green]")
    return [{"reference": ref} for ref in references]

# New function to write unique references back to the TXT file
def write_unique_references_to_txt(input_file, unique_references):
    console.print(f"[bold blue]Writing {len(unique_references)} unique references back to {input_file}[/bold blue]")
    with open(input_file, 'w') as file:
        for ref in unique_references:
            file.write(f"{ref['reference']}\n")
    console.print("[green]Unique references written successfully[/green]")

# Function to write verses to a JSON file
def write_verses_to_json(output_file, verses):
    console.print(f"[bold blue]Writing {len(verses)} verses to {output_file}[/bold blue]")
    with open(output_file, 'w') as file:
        json.dump(verses, file, indent=2)
    console.print("[green]Verses written successfully[/green]")

def is_subset_reference(ref1, ref2):
    """Check if ref1 is a subset of ref2"""
    book1, chapter_verse1 = ref1.rsplit(' ', 1)
    book2, chapter_verse2 = ref2.rsplit(' ', 1)
    
    if book1 != book2:
        return False
    
    chapter1, verse1 = chapter_verse1.split(':')
    chapter2, verse2 = chapter_verse2.split(':')
    
    if chapter1 != chapter2:
        return False
    
    if '-' in verse1:
        start1, end1 = map(int, verse1.split('-'))
    else:
        start1 = end1 = int(verse1)
    
    if '-' in verse2:
        start2, end2 = map(int, verse2.split('-'))
    else:
        start2 = end2 = int(verse2)
    
    return start2 <= start1 and end1 <= end2

def remove_duplicate_references(references):
    unique_refs = OrderedDict()
    removed_count = 0
    
    for ref in references:
        current_ref = ref['reference']
        is_duplicate = False
        
        for existing_ref in list(unique_refs.keys()):
            if is_subset_reference(current_ref, existing_ref):
                is_duplicate = True
                break
            elif is_subset_reference(existing_ref, current_ref):
                del unique_refs[existing_ref]
                unique_refs[current_ref] = ref
                is_duplicate = True
                removed_count += 1
                break
        
        if not is_duplicate:
            unique_refs[current_ref] = ref
    
    return list(unique_refs.values()), removed_count

# Updated main function
def main():
    console.print("[bold magenta]Starting verse extraction process[/bold magenta]")
    
    # Input and output file paths
    input_file = './verse_references.txt'
    output_file = './verses.json'
    
    # Read references from input TXT
    verse_references = read_references_from_txt(input_file)
    
    # Remove duplicate references
    unique_references, removed_count = remove_duplicate_references(verse_references)
    
    # Process the unique verse references
    verses = process_verse_references(unique_references)
    
    # Write the processed verses to output JSON
    write_verses_to_json(output_file, verses)
    
    # Write unique references back to the input TXT file
    write_unique_references_to_txt(input_file, unique_references)
    
    console.print("[bold magenta]Verse extraction process completed[/bold magenta]")
    console.print(f"[bold green]Removed {removed_count} duplicate or overlapping references from {input_file}[/bold green]")

# The function can be called to run the entire process
if __name__ == "__main__":
    main()
