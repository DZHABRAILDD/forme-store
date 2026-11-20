import fs from 'node:fs';
import path from 'node:path';
const base='/forme-store/';
fs.cpSync('dist','docs',{recursive:true});
const files=dir=>fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):[path.join(dir,e.name)]);
for(const filename of files('docs').filter(f=>/\.(html|js|css)$/.test(f))){
  const text=fs.readFileSync(filename,'utf8').replace(/(["'`(])\/(images|fonts|assets)\//g,'$1'+base+'$2/');
  fs.writeFileSync(filename,text);
}
fs.writeFileSync('docs/.nojekyll','');
console.log('GitHub Pages ready at '+base);
