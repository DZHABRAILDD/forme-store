import React,{useEffect,useState} from 'react';
import {heroPhotos as photos} from './editorial';
export default function HeroPhotos(){
 const [active,setActive]=useState(0),[ready,setReady]=useState(()=>photos.map(()=>false));
 const [reduce,setReduce]=useState(()=>matchMedia('(prefers-reduced-motion: reduce)').matches);
 useEffect(()=>{const q=matchMedia('(prefers-reduced-motion: reduce)'),change=()=>setReduce(q.matches);q.addEventListener('change',change);return()=>q.removeEventListener('change',change)},[]);
 useEffect(()=>{if(reduce)return;const timer=setInterval(()=>{if(!document.hidden)setActive(i=>ready[(i+1)%photos.length]?(i+1)%photos.length:i)},3000);return()=>clearInterval(timer)},[reduce,ready]);
 return <div className="hero-photos" aria-label="Фотографии коллекции">{photos.map((p,i)=><img key={p.image} src={p.image} alt={p.alt} aria-hidden={i!==active} className={i===active?'active':''} width={p.width} height={p.height} decoding="async" fetchPriority={i===0?'high':'low'} onLoad={()=>setReady(r=>r.map((v,n)=>n===i?true:v))}/>)}</div>;
}
