/* Small, offline spreadsheet engine. Never evaluates JavaScript or arbitrary code. */
(function(root) {
  'use strict';
  function colIndex(s) { let n=0; for(const c of s.toUpperCase()) n=n*26+c.charCodeAt(0)-64; return n-1; }
  function colName(n) { let s=''; for(n++;n;n=Math.floor((n-1)/26)) s=String.fromCharCode(65+(n-1)%26)+s; return s; }
  function coordinate(ref) { const m=/^\$?([A-Z]+)\$?([1-9]\d*)$/i.exec(ref); if(!m) throw Error('Invalid cell reference'); return [Number(m[2])-1,colIndex(m[1])]; }
  function evaluate(raw, ref, stack=[]) {
    const text=String(raw??'').trim().replace(/×/g,'*').replace(/÷/g,'/').replace(/−/g,'-');
    if(!text) throw Error('Blank cell: enter a number or formula');
    if(text.length>600) throw Error('Formula is too long');
    if(text[0]!=='=') { const v=Number(text.replace(/,/g,'')); if(Number.isFinite(v)) return v; }
    const src=(text[0]==='='?text.slice(1):text).toUpperCase(); let tokens=[],pos=0;
    while(pos<src.length) {
      if(/\s/.test(src[pos])) {pos++;continue;}
      const m=/^(\$?[A-Z]+\$?[1-9]\d*|(?:\d+\.?\d*|\.\d+)(?:E[+-]?\d+)?|[A-Z]+|[+\-*/^(),:%])/.exec(src.slice(pos));
      if(!m) throw Error('Unsupported formula character'); tokens.push(m[0]);pos+=m[0].length;
    }
    let i=0,depth=0;
    const take=t=>{if(tokens[i]!==t) throw Error('Expected '+t); i++;};
    const cell=t=>{ const clean=t.replace(/\$/g,''); coordinate(clean); if(stack.includes(clean)) throw Error('Circular reference at '+clean); if(stack.length>100) throw Error('Reference chain is too long'); return evaluate(ref(clean),ref,[...stack,clean]); };
    function primary() {
      if(++depth>60) throw Error('Formula nesting is too deep');
      let t=tokens[i++],v;
      if(t==='('){v=expr();take(')');}
      else if(t && /^\$?[A-Z]+\$?\d+$/.test(t)) v=cell(t);
      else if(t && /^(\d|\.)/.test(t)) v=Number(t);
      else if(['SUM','AVERAGE','MIN','MAX','EXP','LN','ABS','SQRT','ROUND'].includes(t)) {
        take('(');const args=[];
        if(tokens[i]!==')') do {
          if(/^\$?[A-Z]+\$?\d+$/.test(tokens[i]||'') && tokens[i+1]===':') {
            const a=coordinate(tokens[i]),b=coordinate(tokens[i+2]);i+=3;
            if(b[0]<a[0]||b[1]<a[1]||(b[0]-a[0]+1)*(b[1]-a[1]+1)>1000) throw Error('Invalid or oversized range');
            for(let r=a[0];r<=b[0];r++) for(let c=a[1];c<=b[1];c++) args.push(cell(colName(c)+(r+1)));
          } else args.push(expr());
          if(tokens[i]!==',') break;i++;
        } while(true);
        take(')');
        if(!args.length) throw Error('Function needs arguments');
        if(['EXP','LN','ABS','SQRT'].includes(t)&&args.length!==1) throw Error(t+' needs one argument');
        if(t==='ROUND'&&(args.length!==2||!Number.isInteger(args[1])||Math.abs(args[1])>12)) throw Error('Use ROUND(value, digits), up to 12 digits');
        const sum=()=>args.reduce((a,b)=>a+b,0);
        const f={SUM:sum,AVERAGE:()=>sum()/args.length,MIN:()=>Math.min(...args),MAX:()=>Math.max(...args),EXP:()=>Math.exp(args[0]),LN:()=>Math.log(args[0]),ABS:()=>Math.abs(args[0]),SQRT:()=>Math.sqrt(args[0]),ROUND:()=>Math.sign(args[0])*Math.round(Math.abs(args[0])*10**args[1])/10**args[1]};v=f[t]();
      } else throw Error('Use a cell, number, or supported function');
      while(tokens[i]==='%'){i++;v/=100;} depth--;return v;
    }
    function unary(){if(tokens[i]==='+'){i++;return unary();}if(tokens[i]==='-'){i++;return -unary();}return power();}
    function power(){let v=primary();if(tokens[i]==='^'){i++;v=v**unary();}return v;}
    function term(){let v=unary();while(['*','/'].includes(tokens[i])){const op=tokens[i++],b=unary();if(op==='/'&&b===0)throw Error('Cannot divide by zero');v=op==='*'?v*b:v/b;}return v;}
    function expr(){let v=term();while(['+','-'].includes(tokens[i])){const op=tokens[i++],b=term();v=op==='+'?v+b:v-b;}return v;}
    const result=expr(); if(i!==tokens.length) throw Error('Unexpected formula text');if(!Number.isFinite(result))throw Error('Result is not a finite number');return result;
  }
  function shift(formula,rows,cols=0) {
    return String(formula).replace(/(?<![A-Z0-9_.])(\$?)([A-Z]+)(\$?)([1-9]\d*)/gi,(_,ac,c,ar,r)=>{const ci=colIndex(c)+(ac?0:cols),ri=Number(r)+(ar?0:rows);if(ci<0||ri<1)throw Error('Reference would move outside the sheet');return ac+colName(ci)+ar+ri;});
  }
  const api={evaluate,shift,coordinate,colName}; if(typeof module!=='undefined') module.exports=api; root.SheetMath=api;
})(typeof window!=='undefined'?window:globalThis);
