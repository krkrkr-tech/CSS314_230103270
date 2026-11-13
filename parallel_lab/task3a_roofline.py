import argparse, multiprocessing as mp, time
from multiprocessing import shared_memory
from harness import emit_verify_tag, physical_cores, run_benchmark

def copy_worker(name_a,name_b,start,end):
    a=shared_memory.SharedMemory(name_a); b=shared_memory.SharedMemory(name_b)
    try: a.buf[start:end]=b.buf[start:end]
    finally: a.close(); b.close()
def fma_worker(iters, results):
    vals=[1.0]*16
    for i in range(iters//16):
        for j in range(16): vals[j]=vals[j]*1.0000001+0.1
    results.put(sum(vals))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--bytes",type=int,default=96_000_000); ap.add_argument("--flops",type=int,default=80_000_000); ap.add_argument("--processes",type=int,default=physical_cores()); ap.add_argument("--runs",type=int,default=3); ap.add_argument("--student-id",default="230103270")
    a=ap.parse_args(); p=max(1,a.processes); size=a.bytes; aa=shared_memory.SharedMemory(create=True,size=size); bb=shared_memory.SharedMemory(create=True,size=size)
    try:
        def copy(): 
            jobs=[mp.Process(target=copy_worker,args=(aa.name,bb.name,i*size//p,(i+1)*size//p)) for i in range(p)]
            for j in jobs:j.start()
            for j in jobs:j.join()
        bw=run_benchmark(copy,1,a.runs).median_ms; gb=2*size/(bw/1000)/1e9
    finally: aa.close();aa.unlink();bb.close();bb.unlink()
    def compute():
        results=mp.Queue()
        jobs=[mp.Process(target=fma_worker,args=(a.flops//p,results)) for _ in range(p)]
        for j in jobs:j.start()
        for j in jobs:j.join()
        if any(j.exitcode for j in jobs):
            raise RuntimeError("FMA worker failed")
        for _ in jobs:
            results.get()
        results.close()
        results.join_thread()
    fs=run_benchmark(compute,1,a.runs).median_ms
    gflop=a.flops/(fs/1000)/1e9
    print(f"BW_sustained_GBps={gb:.6f} P_sustained_GFLOPs={gflop:.6f} ridge_point={gflop/gb:.6f}")
    print(emit_verify_tag("PHASE3",a.student_id,gb,gflop))
if __name__=="__main__": mp.freeze_support();main()
