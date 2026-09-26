import {chromium} from 'playwright';
import fs from 'node:fs/promises';
const browser=await chromium.launch({channel:'chrome',headless:true});
const page=await browser.newPage({viewport:{width:1600,height:1100},deviceScaleFactor:2});
async function open(route){await page.goto('https://fearandgreedgraph.com'+route,{waitUntil:'domcontentloaded'});await page.waitForTimeout(6000);const c=page.getByRole('button',{name:'Close Whats New',exact:true});if(await c.count())await c.click();}
async function shot(n){await page.screenshot({path:'assets/'+n+'.png'});console.log(n);}
await open('/');
await page.locator('.gauge-left').screenshot({path:'assets/gauge-close.png'});
await page.evaluate(()=>window.scrollTo(0,document.querySelector('.layout').offsetTop-20));
await shot('compare-spy');
await page.locator('button').filter({hasText:'Nvidia'}).first().click();
await page.waitForTimeout(6500);
await shot('compare-nvda');
await page.getByRole('button',{name:'6m',exact:true}).click();await page.waitForTimeout(700);
await shot('compare-6m');
await open('/screener');
console.log('selectors',await page.locator('select').evaluateAll(es=>es.slice(0,2).map(e=>({aria:e.getAttribute('aria-label'),options:[...e.options].slice(0,8).map(o=>({v:o.value,t:o.text}))}))));
const marketCap=page.locator('select').filter({has:page.locator('option').filter({hasText:'Mega'})}).first();
await marketCap.selectOption({index:1});
await shot('screener-filter');
await page.getByRole('button',{name:'Find & search',exact:true}).click();
await page.waitForTimeout(15000);
await shot('screener-result');
await fs.writeFile('assets/screener-result.txt',await page.locator('body').innerText());
await open('/hedge-funds/CITADELADVISORS');
await shot('holdings');
await fs.writeFile('assets/holdings.txt',await page.locator('body').innerText());
console.log('holdings structure',await page.locator('h1,h2,table').evaluateAll(es=>es.map(e=>({tag:e.tagName,text:e.textContent.slice(0,80),box:e.getBoundingClientRect().toJSON()}))));
await open('/stock/NVDA');
console.log('watch buttons',await page.locator('button').filter({hasText:/watchlist/i}).allTextContents());
await shot('stock-save');
const logo=await page.locator('header img.logo').getAttribute('src');
const resp=await page.request.get(new URL(logo,page.url()).href);await fs.writeFile('assets/brand-mark.png',await resp.body());
const add=page.getByRole('button',{name:'Add to watchlist',exact:false}).first();
if(await add.count()){await add.click();await page.waitForTimeout(400);await shot('save-signin');}
await browser.close();
