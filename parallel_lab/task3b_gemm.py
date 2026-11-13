import argparse, multiprocessing as mp, time
from multiprocessing import shared_memory
from harness import emit_verify_tag, run_benchmark

def gemm_worker(name_a,name_b,name_c,n,lo,hi,variant,bs):
    a=shared_memory.SharedMemory(name_a);b=shared_memory.SharedMemory(name_b);c=shared_memory.SharedMemory(name_c)
    try:
        A=a.buf.cast("d");B=b.buf.cast("d");C=c.buf.cast("d")
        if variant==1:
            for i in range(lo,hi):
                for j in range(n):
                    x=0.0
                    for k in range(n):x+=A[i*n+k]*B[k*n+j]
                    C[i*n+j]=x
        elif variant==2:
            for i in range(lo,hi):
                for k in range(n):
                    x=A[i*n+k]
                    for j in range(n): C[i*n+j]+=x*B[k*n+j]
        else:
            # Rows are partitioned between workers; tiles keep A, B and C
            # submatrices reusable while the inner j loop remains contiguous.
            for ii in range(lo, hi, bs):
                for jj in range(0, n, bs):
                    for kk in range(0, n, bs):
                        for i in range(ii, min(ii + bs, hi)):
                            for k in range(kk, min(kk + bs, n)):
                                x = A[i*n+k]
                                for j in range(jj, min(jj + bs, n)):
                                    C[i*n+j] += x * B[k*n+j]
        del A,B,C
    finally:a.close();b.close();c.close()
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--n",type=int,default=384);ap.add_argument("--processes",type=int,default=min(4,mp.cpu_count()));ap.add_argument("--runs",type=int,default=1);ap.add_argument("--student-id",default="230103270");a=ap.parse_args()
    n=a.n;p=max(1,a.processes); sizes=[4,8,12,16,24,32,48,64,96,128]; A=shared_memory.SharedMemory(create=True,size=8*n*n);B=shared_memory.SharedMemory(create=True,size=8*n*n)
    try:
        import array; av=array.array("d",[0.001]*(n*n));bv=array.array("d",[0.002]*(n*n)); A.buf[:]=av.tobytes();B.buf[:]=bv.tobytes()
        def bench(v,bs=0):
            C=shared_memory.SharedMemory(create=True,size=8*n*n);C.buf[:]=bytes(8*n*n)
            def work():
                jobs=[mp.Process(target=gemm_worker,args=(A.name,B.name,C.name,n,i*n//p,(i+1)*n//p,v,bs)) for i in range(p)]
                for j in jobs:j.start()
                for j in jobs:j.join()
            s=run_benchmark(work,0,a.runs);C.close();C.unlink();return s
        first=bench(1).median_ms; second=bench(2).median_ms; print(f"variant1_ms={first:.3f} variant2_ms={second:.3f}")
        best=(0,0.0)
        for bs in sizes:
            ms=bench(3,bs).median_ms; g=2*n**3/(ms*1e6); print(f"BS={bs} footprint_bytes={3*bs*bs*8} median_ms={ms:.3f} GFLOPs={g:.6f}")
            if g>best[1]:best=(bs,g)
        print(emit_verify_tag("PHASE3",a.student_id,2*n**3/(first*1e6),best[1]))
    finally:A.close();A.unlink();B.close();B.unlink()
if __name__=="__main__":mp.freeze_support();main()
