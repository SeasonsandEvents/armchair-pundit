import json,glob,os,re,random,yaml
SRC='/home/claude/src106/epl'
o=json.load(open(f'{SRC}/engine/clue_overrides.json'))
book=yaml.safe_load(open(f'{SRC}/engine/book.yaml'))
by={}
for f in glob.glob(f'{SRC}/engine/cache/*.json'):
    by.setdefault(int(os.path.basename(f)[:2]),[]).append(f)
latest={n:max(fs,key=os.path.getmtime) for n,fs in by.items()}

def build(words, seed, maxside):
    rnd=random.Random(seed); ws=words[:]; ws.sort(key=lambda w:-len(w['w'])); first=ws[0]; rest=ws[1:]; rnd.shuffle(rest); ws=[first]+rest
    grid={}; placed=[]
    def ok(w,r,c,d):
        dr,dc=(0,1) if d=='A' else (1,0); cross=0
        if grid.get((r-dr,c-dc)) or grid.get((r+dr*len(w),c+dc*len(w))): return -1
        for i,ch in enumerate(w):
            rr,cc=r+dr*i,c+dc*i; g=grid.get((rr,cc))
            if g:
                if g[0]!=ch or d in g[1]: return -1
                cross+=1
            else:
                if d=='A' and (grid.get((rr-1,cc)) or grid.get((rr+1,cc))): return -1
                if d=='D' and (grid.get((rr,cc-1)) or grid.get((rr,cc+1))): return -1
        return cross
    def bounds(extra=()):
        ks=list(grid)+list(extra); rs=[k[0] for k in ks]; cs=[k[1] for k in ks]; return max(rs)-min(rs)+1,max(cs)-min(cs)+1
    def put(e,r,c,d):
        w=e['w'];dr,dc=(0,1) if d=='A' else (1,0)
        for i,ch in enumerate(w):
            k=(r+dr*i,c+dc*i); g=grid.get(k); grid[k]=(ch,(g[1] if g else '')+d)
        placed.append(dict(e,r=r,c=c,d=d))
    put(first,0,0,'A'); left=ws[1:]
    for _ in range(3):
        nxt=[]
        for e in left:
            w=e['w'];best=None
            for (r,c),(ch,_) in list(grid.items()):
                for i,x in enumerate(w):
                    if x!=ch: continue
                    for d in 'AD':
                        rr,cc=(r,c-i) if d=='A' else (r-i,c)
                        s=ok(w,rr,cc,d)
                        if s>0:
                            cellsx=[(rr+(k if d=='D' else 0),cc+(k if d=='A' else 0)) for k in range(len(w))]
                            h,wd=bounds(cellsx)
                            if max(h,wd)>maxside: continue
                            sc=s*10-h*wd*0.05
                            if best is None or sc>best[0]: best=(sc,rr,cc,d)
            if best: put(e,best[1],best[2],best[3])
            else: nxt.append(e)
        left=nxt
    rs=[k[0] for k in grid]; cs=[k[1] for k in grid]
    for p in placed: p['r']-=min(rs); p['c']-=min(cs)
    return placed,max(rs)-min(rs)+1,max(cs)-min(cs)+1

def runs_ok(pl,h,w):
    g={}
    for p in pl:
        for i,ch in enumerate(p['w']): g[(p['r']+(i if p['d']=='D' else 0),p['c']+(i if p['d']=='A' else 0))]=ch
    runs=set()
    for r in range(h):
        c=0
        while c<w:
            if (r,c) in g:
                s=c
                while (r,c) in g: c+=1
                if c-s>1: runs.add(('A',r,s))
            c+=1
    for c in range(w):
        r=0
        while r<h:
            if (r,c) in g:
                s=r
                while (r,c) in g: r+=1
                if r-s>1: runs.add(('D',s,c))
            r+=1
    return runs=={(p['d'],p['r'],p['c']) for p in pl}

def norm(s): return re.sub(r'[^A-Z]','',s.upper())
out=[];report=[]
for idx,pz in enumerate(book['puzzles'],start=1):
    fname=pz['facts']; ov=o.get(fname,{})
    d=json.load(open(latest[idx]))
    ents=[]
    for e in d['entries']:
        disp=e['display']; clue=ov.get(disp,e['clue'])
        w=norm(disp)
        enum=','.join(str(len(x)) for x in disp.split()) if ' ' in disp else str(len(w))
        if len(w)>13 or len(w)<3: continue
        if w in norm(clue): continue
        ents.append(dict(w=w,clue=clue,enum=enum,display=disp))
    best=None
    for (minw,maxside,poolsz,tries) in [(12,13,14,1500),(12,15,16,1500),(11,15,18,2000)]:
        for seed in range(tries):
            rnd=random.Random(seed*7+idx); pool=ents[:]; rnd.shuffle(pool); pool=pool[:poolsz]
            pl,h,wd=build(pool,seed,maxside)
            if len(pl)<minw: continue
            if not runs_ok(pl,h,wd): continue
            answers=[p['display'] for p in pl]
            bad=any(any(len(a)>3 and a.lower() in p['clue'].lower() for a in answers if a!=p['display']) for p in pl)
            if bad: continue
            sc=min(len(pl),14)*100-abs(h-wd)*4-h*wd*0.6
            if best is None or sc>best[0]: best=(sc,pl,h,wd)
        if best: break
    if not best:
        report.append(f"{pz['title']}: FAILED"); continue
    _,pl,h,wd=best
    title=f"England's top flight, {pz['title']}"
    out.append(dict(title=title,kind='football',rows=h,cols=wd,words=[{k:p[k] for k in ('w','clue','enum','r','c','d')} for p in pl]))
    report.append(f"{pz['title']}: {len(pl)} words {h}x{wd} (from {len(ents)} checked clues)")
json.dump(out,open('/home/claude/apx/football.json','w'),ensure_ascii=False)
print('\n'.join(report))
