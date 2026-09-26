import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const browser=await chromium.launch({channel:'chrome',headless:true});
const context=await browser.newContext({viewport:{width:1600,height:1100},deviceScaleFactor:2});
const page=await context.newPage();
const out=path.join(root,'assets');
const records=[];
async function open(route,name){
 await page.goto('https://fearandgreedgraph.com'+route,{waitUntil:'domcontentloaded',timeout:60000});
 await page.waitForTimeout(6500);
 const close=page.getByRole('button',{name:'Close Whats New',exact:true}); if(await close.count())await close.click();
 await page.evaluate(()=>document.fonts.ready);
 await page.screenshot({path:path.join(out,name+'.png')});
 await fs.writeFile(path.join(out,name+'.txt'),await page.locator('body').innerText());
 records.push({name,url:page.url(),captured:new Date().toISOString()});
 console.log('Captured',name);
}
await open('/','home');
await page.locator('.gauge-wrap').screenshot({path:path.join(out,'gauge.png')});
const nv=page.getByRole('button',{name:'NvidiaNVDA',exact:true});
if(await nv.count()) {await nv.click();await page.waitForTimeout(4500);}
await page.locator('.layout').scrollIntoViewIfNeeded();
await page.evaluate(()=>window.scrollTo(0,document.querySelector('.layout').getBoundingClientRect().top+window.scrollY-30));
await page.screenshot({path:path.join(out,'compare-nvda.png')});
const six=page.getByRole('button',{name:'6m',exact:true});if(await six.count()){await six.click();await page.waitForTimeout(700);}
await page.screenshot({path:path.join(out,'compare-6m.png')});
await page.getByRole('button',{name:'Lilo AI',exact:true}).click();
await page.getByRole('textbox',{name:'Ask Lilo AI'}).fill('Where can I compare stocks?');
await page.getByRole('textbox',{name:'Ask Lilo AI'}).press('Enter');
await page.waitForTimeout(16000);
await page.locator('.lilo-panel').screenshot({path:path.join(out,'lilo.png')});
await fs.writeFile(path.join(out,'lilo.txt'),await page.locator('.lilo-panel').innerText());
await open('/maps','maps');
await open('/screener','screener');
await open('/hedge-funds','funds');
await fs.writeFile(path.join(out,'fund-links.json'),JSON.stringify(await page.locator('a[href^="/hedge-funds/"]').evaluateAll(es=>es.slice(0,12).map(e=>({href:e.getAttribute('href'),text:e.innerText}))),null,2));
await open('/watchlist','watchlist');
await fs.writeFile(path.join(out,'capture-manifest.json'),JSON.stringify(records,null,2));
await browser.close();
