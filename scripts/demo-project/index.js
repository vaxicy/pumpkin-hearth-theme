// Pumpkin Hearth Theme — cream paper, pumpkin, coffee and wood
import { readFile } from 'node:fs/promises';

const HEARTH_PALETTE = {
  pumpkin: '#E07A2E',
  ember: '#C05A24',
  cream: '#FFF7E6',
  coffee: '#4A2A1A',
  wood: '#8A5A12',
};

export class Hearth {
  constructor(name = 'Autumn evening') {
    this.name = name;
    this.colors = Object.values(HEARTH_PALETTE);
  }

  /** Blend two colors into a warm shade. */
  mix(from, to, ratio = 0.5) {
    const parse = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
    const [a, b] = [parse(from), parse(to)];
    const channels = a.map((value, i) => Math.round(value * (1 - ratio) + b[i] * ratio));
    return '#' + channels.map((value) => value.toString(16).padStart(2, '0')).join('');
  }

  async describe(file) {
    const content = await readFile(file, 'utf8');
    return { name: this.name, colors: this.colors, content };
  }
}

const hearth = new Hearth();
console.log(hearth.mix(HEARTH_PALETTE.pumpkin, HEARTH_PALETTE.cream));
