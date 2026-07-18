const fs = require('fs');
const path = require('path');

let data = '';
process.stdin.on('data', (chunk) => { data += chunk; });
process.stdin.on('end', () => {
  try {
    const input = JSON.parse(data);
    const prompt = input.prompt || '';
    const timestamp = new Date().toISOString();
    const target = path.join(__dirname, '..', '..', 'sentiment-lab', 'PROMPTS.md');
    fs.appendFileSync(target, `\n## ${timestamp}\n\n${prompt}\n`);
  } catch (e) {}
});
