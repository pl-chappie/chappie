# chappie #

`chappie` is a runtime observer for Java that collects data for the functional state of an executed program at the thread level. Collected data spans the thread, application, and system levels, indexed by an integer epoch.

## Utilities ##

`chappie` uses the following libraries for sampling:

#### [jRAPL](http://kliu20.github.io/jRAPL) ####
Java wrapper for Intel's [RAPL](https://en.wikipedia.org/w/index.php?title=Running_average_power_limit&redirect=yes) interface used to make per socket energy measurements.

#### [GLIBC](https://www.gnu.org/software/libc/) ####
Library tools for Linux systems. We use the syscall interface to get process and thread ids at runtime.

#### [javassist](http://www.javassist.org/) ####
Java bytecode manipulation library. **javassist** allows for runtime instrumentation of java classes. We instrument all classes that implement [java.lang.Runnable](https://docs.oracle.com/javase/8/docs/api/java/lang/Runnable.html) to add their thread id to an internal map before calling `run()`.

#### [Honest Profiler](https://github.com/jvm-profiling-tools/honest-profiler) ####
A Java profiler that reduces the overhead incurred from traditional profilers by leveraging the JVM. It implements asynchronous stack fetching for threads to remove the inherent overhead from safepoints that are required for [getStackTrace()](https://docs.oracle.com/javase/8/docs/api/java/lang/Thread.html).

## Building ##

`$ ant jar` at the top level builds `chappie.jar`, which contains all the necessary requirements to run chappie around a program.

## Running ##

GLIBC is required to run chappie. This can be installed with a package manager or built from source.

`chappie` initializes an observer, bootstraps the program, and performs clean up. Command line arguments are used to direct chappie but it is recommended instead to use `run/run.sh`. The call signature for `run/run.sh` is:

run/run.sh <jar_path> <extra_jars> <jar_main_class> <args>

In addition, a small test program is provided at `test`

## Output ##

At program termination, the chaperone writes all observations to two `.csv` files. `chappie.trace.csv` contains a long-format time series of the number of threads for each Java activity state. `chappie.thread.csv` contains a long-format time-series of differential package and DRAM energy consumption and differential memory consumption for each thread. These are formatted for ease of use in R or csv manipulation, such as `pandas`. More details regarding results can be found in the [wiki](https://github.com/anthonycanino1/chappie/wiki/Scripts-and-Figure-Generation).
