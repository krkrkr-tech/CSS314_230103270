import argparse, math, multiprocessing as mp
from harness import emit_verify_tag, run_benchmark

def kernel(lo_hi):
    lo, hi = lo_hi; total = 0.0
    for i in range(lo, hi):
        x = (i % 97) * 0.001 + 1.0
        for _ in range(35):
            x = x * 1.000001 + math.sin(x) * 0.00001
        total += x
    return total

def serial_stage(n):
    return sum(math.sqrt(abs(math.sin(i * .001)) + 1.0)
               for i in range(max(1, int(n * .05))))

def trial(pool, n, p):
    serial_stage(n)
    step = (n + p - 1) // p
    return sum(pool.map(kernel, [(i, min(n, i + step)) for i in range(0, n, step)]))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--n",type=int,default=1_600_000)
    ap.add_argument("--n0",type=int,default=250_000); ap.add_argument("--max-processes",type=int,default=mp.cpu_count())
    ap.add_argument("--runs",type=int,default=3); ap.add_argument("--warmup",type=int,default=1); ap.add_argument("--student-id",default="230103270")
    a=ap.parse_args(); maxp=max(1,min(a.max_processes,mp.cpu_count())); strong={}
    with mp.Pool(maxp) as pool:
        for p in range(1,maxp+1):
            stat=run_benchmark(lambda p=p: trial(pool,a.n,p),a.warmup,a.runs); strong[p]=stat.median_ms
            print(f"strong p={p} N={a.n} median_ms={stat.median_ms:.3f} speedup={strong[1]/stat.median_ms:.3f} efficiency={strong[1]/stat.median_ms/p:.3f}")
        weak={}
        for p in range(1,maxp+1):
            stat=run_benchmark(lambda p=p: trial(pool,a.n0*p,p),a.warmup,a.runs); weak[p]=stat.median_ms
            print(f"weak p={p} N={a.n0*p} median_ms={stat.median_ms:.3f} gustafson={p-(weak[1]/stat.median_ms)*(p-1):.3f}")
    print(emit_verify_tag("PHASE2",a.student_id,strong[maxp],maxp-(weak[1]/weak[maxp])*(maxp-1)))
if __name__=="__main__":
    mp.freeze_support(); main()
