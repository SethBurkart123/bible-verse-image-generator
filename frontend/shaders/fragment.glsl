uniform sampler2D tDiffuse;
varying vec2 vUv;
uniform float vignetteSize;
uniform float vignetteIntensity;
uniform float vignetteBlur;
uniform float grainIntensity;
uniform float grainSize;
uniform float brightness;
uniform vec2 resolution;
uniform int blendMode;

float random(vec2 p) {
  return fract(sin(dot(p, vec2(12.9898,78.233))) * 43758.5453);
}

vec3 applyBlendMode(vec3 base, vec3 blend) {
    if (blendMode == 1) { // Lighten
        return max(base, blend);
    } else if (blendMode == 2) { // Screen
        return 1.0 - (1.0 - base) * (1.0 - blend);
    } else if (blendMode == 3) { // Color Dodge
        return base / (1.0 - blend);
    } else if (blendMode == 4) { // Linear Dodge (Add)
        return base + blend;
    } else if (blendMode == 5) { // Overlay
        return mix(2.0 * base * blend, 1.0 - 2.0 * (1.0 - base) * (1.0 - blend), step(0.5, base));
    } else if (blendMode == 6) { // Soft Light
        return mix(2.0 * base * blend + base * base * (1.0 - 2.0 * blend), sqrt(base) * (2.0 * blend - 1.0) + 2.0 * base * (1.0 - blend), step(0.5, blend));
    } else if (blendMode == 7) { // Hard Light
        return mix(2.0 * base * blend, 1.0 - 2.0 * (1.0 - base) * (1.0 - blend), step(0.5, blend));
    }
    return blend; // Normal blend (or any unrecognized mode)
}

void main() {
  vec4 texel = texture2D(tDiffuse, vUv);
  
  // Vignette effect with enhanced blur
  vec2 center = vec2(0.5, 0.5);
  float dist = distance(vUv, center);
  float vignette = smoothstep(vignetteSize, vignetteSize - vignetteBlur * 0.005, dist);
  
  vec4 blurredTexel = vec4(0.0);
  float totalWeight = 0.0;
  float blurSize = vignetteBlur * 0.0005;
  int samples = 16; // Stronger blur

  for (int i = 0; i < samples; i++) {
    float angle = float(i) * (2.0 * 3.14159 / float(samples));
    vec2 offset = vec2(cos(angle), sin(angle)) * blurSize;
    
    // Clamp the sampling coordinates to prevent wrapping
    vec2 sampleCoord = clamp(vUv + offset, vec2(0.0), vec2(1.0));
    
    float weight = 1.0 - smoothstep(0.0, 1.0, length(offset) / blurSize);
    blurredTexel += texture2D(tDiffuse, sampleCoord) * weight;
    totalWeight += weight;
  }
  blurredTexel /= totalWeight;

  // Adjust the mix factor to reduce the visibility of the blur at the edges
  float blurMixFactor = smoothstep(0.0, vignetteSize, dist);
  texel = mix(texel, blurredTexel, blurMixFactor * vignette);
  
  // Apply vignette darkening
  texel.rgb *= mix(1.0, vignette, vignetteIntensity);

  // Updated Grain effect with color-dodge blend mode
  vec2 grainUv = vUv * grainSize * resolution / 100.0;
  float noise = random(grainUv);
  vec3 grain = vec3(noise);

  // Apply the selected blend mode for grain
  vec3 blendedGrain = applyBlendMode(texel.rgb, grain);
  texel.rgb = mix(texel.rgb, blendedGrain, grainIntensity);

  // Apply brightness
  texel.rgb *= brightness;

  gl_FragColor = texel;
}