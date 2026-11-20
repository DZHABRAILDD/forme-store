import fs from 'node:fs';
fs.cpSync('dist','docs',{recursive:true});
fs.writeFileSync('docs/.nojekyll','');
console.log('GitHub Pages ready: docs/');
