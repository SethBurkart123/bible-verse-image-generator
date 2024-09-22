uniform sampler2D tDiffuse;
varying vec2 vUv;
uniform float vignetteSize;
uniform float vignetteIntensity;
uniform float vignetteBlur;
uniform float dreamyBlur;
uniform float dreamyBlurSize;
uniform float dreamyBlurIntensity;
uniform float grainIntensity;
uniform float grainSize;
uniform float brightness;
uniform vec2 resolution;
uniform int blendMode;
uniform float dreamyVignetteSize;
uniform float dreamyVignetteIntensity;
uniform float chromaticAberration;

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
  vec2 uv = vUv;
  vec2 center = vec2(0.5, 0.5);
  
  // Chromatic aberration
  vec2 caOffset = (uv - center) * chromaticAberration;
  vec4 texelR = texture2D(tDiffuse, uv - caOffset);
  vec4 texelG = texture2D(tDiffuse, uv);
  vec4 texelB = texture2D(tDiffuse, uv + caOffset);
  vec4 texel = vec4(texelR.r, texelG.g, texelB.b, (texelR.a + texelG.a + texelB.a) / 3.0);
  
  // Vignette effect
  float dist = distance(uv, center);
  float vignette = smoothstep(vignetteSize, vignetteSize - vignetteBlur * 0.005, dist);
  
  // Dreamy blur effect
  vec4 blurredTexel = vec4(0.0);
  float totalWeight = 0.0;
  float blurSize = dreamyBlurSize * 0.05;
  int samples = 16;

  for (int i = 0; i < samples; i++) {
    float angle = float(i) * (2.0 * 3.14159 / float(samples));
    vec2 offset = vec2(cos(angle), sin(angle)) * blurSize;
    
    // Use the distance from the center to vary the blur intensity
    float blurFactor = smoothstep(0.0, 1.0, dist / (dreamyBlurSize * 0.5));
    vec2 sampleCoord = uv + offset * blurFactor;
    
    float weight = 1.0 - smoothstep(0.0, 1.0, length(offset) / blurSize);
    blurredTexel += texture2D(tDiffuse, sampleCoord) * weight;
    totalWeight += weight;
  }
  blurredTexel /= totalWeight;

  // Dreamy vignette mask (inverted to apply more strongly to the outside)
  float dreamyVignette = smoothstep(0.0, dreamyVignetteSize, dist);
  
  // Mix the original texel with the blurred texel based on dreamyBlur, dreamyBlurIntensity, and dreamyVignette
  texel = mix(texel, blurredTexel, dreamyBlur * dreamyBlurIntensity * dreamyVignette);
  
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