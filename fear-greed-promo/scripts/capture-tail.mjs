import {chromium} from 'playwright';
import fs from 'node:fs/promises';
const b=await chromium.launch({channel:'chrome',headless:true});
const p=await b.newPage({viewport:{width:1600,height:1100},deviceScaleFactor:2});
async function go(u){await p.goto('https://fearandgreedgraph.com'+u,{waitUntil:'domcontentloaded'});await p.waitForTimeout(5500);const c=p.getByRole('button',{name:'Close Whats New',exact:true});if(await c.count())await c.click();}
await go('/hedge-funds/CITADELADVISORS');
await p.evaluate(()=>window.scrollTo(0,document.querySelector('table').getBoundingClientRect().top+window.scrollY-210));
await p.screenshot({path:'assets/holdings-table.png'});
await go('/stock/NVDA');
const add=p.locator('button').filter({hasText:'Add to watchlist'}).first();
console.log('save target',await add.boundingBox());
await add.click();await p.waitForTimeout(600);
await p.screenshot({path:'assets/save-signin.png'});
await fs.writeFile('assets/save-signin.txt',await p.locator('body').innerText());
console.log('tail captures complete');
await b.close();
