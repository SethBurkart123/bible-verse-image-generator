uniform sampler2D tDiffuse;
varying vec2 vUv;
uniform float vignetteSize;
uniform float vignetteIntensity;
uniform float vignetteBlur;
uniform float grainIntensity;
uniform float grainSize;
uniform float brightness;
uniform vec2 resolution;

float random(vec2 p) {
  return fract(sin(dot(p, vec2(12.9898,78.233))) * 43758.5453);
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
    float weight = 1.0 - smoothstep(0.0, 1.0, length(offset) / blurSize);
    blurredTexel += texture2D(tDiffuse, vUv + offset) * weight;
    totalWeight += weight;
  }
  blurredTexel /= totalWeight;

  texel = mix(blurredTexel, texel, vignette);
  texel.rgb *= mix(1.0, vignette, vignetteIntensity);

  // Grain effect
  vec2 grainUv = vUv * grainSize * resolution / 100.0;
  float noise = random(grainUv);
  vec3 grain = vec3(noise) * grainIntensity;
  texel.rgb = mix(texel.rgb, grain, grainIntensity);

  // Apply brightness
  texel.rgb *= brightness;

  gl_FragColor = texel;
}