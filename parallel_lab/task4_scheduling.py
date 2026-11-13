import argparse, math, multiprocessing as mp, time
from harness import emit_verify_tag

def cost(i):
    x=0.1
    for j in range(1+(i//60)**2): x=math.sin(x)+math.cos(x)+math.sqrt(abs(x)+1)
    return x
def worker_static(indices, telemetry, slot):
    t=time.perf_counter(); sum(cost(i) for i in indices); telemetry[slot]=(time.perf_counter()-t)*1000
def worker_dynamic(counter,lock,n,chunk,telemetry,slot):
    t=time.perf_counter()
    while True:
        with lock:
            start=counter.value;counter.value+=chunk
        if start>=n:break
        for i in range(start,min(n,start+chunk)):cost(i)
    telemetry[slot]=(time.perf_counter()-t)*1000
def run(n,p,kind,chunk=1):
    telemetry=mp.Array("d",p); jobs=[]
    if kind=="block": jobs=[mp.Process(target=worker_static,args=(range(i*n//p,(i+1)*n//p),telemetry,i)) for i in range(p)]
    elif kind=="cyclic": jobs=[mp.Process(target=worker_static,args=(range(i,n,p),telemetry,i)) for i in range(p)]
    else:
        counter=mp.Value("i",0);lock=mp.Lock();jobs=[mp.Process(target=worker_dynamic,args=(counter,lock,n,chunk,telemetry,i)) for i in range(p)]
    t=time.perf_counter()
    for j in jobs:j.start()
    for j in jobs:j.join()
    wall=(time.perf_counter()-t)*1000; vals=list(telemetry); return wall,max(vals)/(sum(vals)/p) if sum(vals) else 0
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--n",type=int,default=12000);ap.add_argument("--processes",type=int,default=min(4,mp.cpu_count()));ap.add_argument("--student-id",default="230103270");a=ap.parse_args();p=max(1,a.processes)
    b=run(a.n,p,"block");print(f"block wall_ms={b[0]:.3f} lambda={b[1]:.4f}")
    cyc=run(a.n,p,"cyclic");print(f"cyclic wall_ms={cyc[0]:.3f} lambda={cyc[1]:.4f}"); best=None
    for c in (1,4,16,64,256,1024):
        r=run(a.n,p,"dynamic",c);print(f"dynamic chunk={c} wall_ms={r[0]:.3f} lambda={r[1]:.4f}")
        if best is None or r[0]<best[0]:best=(r[0],c)
    print(emit_verify_tag("PHASE4",a.student_id,b[0],best[0]))
if __name__=="__main__":mp.freeze_support();main()
