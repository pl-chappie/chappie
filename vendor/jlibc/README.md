# `jlibc`
wrapper of glibc in java and some high-level constructs to represent the OS.

## `libc`

### native methods
`jlib.libc` exposes [`getpid`](http://man7.org/linux/man-pages/man2/getpid.2.html) and [`gettid`](http://man7.org/linux/man-pages/man2/gettid.2.html) with some error checking for unavailable code. It isn't necessary to use these methods; they are provided for completeness.

### `libc` API
The camel case methods wrap around the native methods and store seen values into a cache. Since the os ids do not change during runtime, we are guaranteed a one-to-one mapping up to `Long.MAX_VALUE`.

`getProcessId` retrieves the pid from a static field.

`getTaskId` returns the tid of the calling thread. If `getTaskId` has already been called, we can use a cached value from a java tid - os tid map; otherwise, we cache the ids to the map.

`getTaskId(Thread)` and `getTIDs` provide access to mapped threads from any thread. This is useful if you want to merge jvm and os data.

## `libc.proc`
Inspired from [psutil](https://github.com/giampaolo/psutil), `libc.proc` exposes a small portion of [proc](http://man7.org/linux/man-pages/man5/proc.5.htmlstat to track cpu and task jiffies.

### Task
`Task` provide the state, current state and socket, and consumed jiffies as reported in `/proc/[pid]/task/[tid]/stat`. This API is design to resemble [java.lang.Thread](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/Thread.html).

### CPU
`CPU` provides the consumed jiffies for a cpu (computation sockets).

## building

`jlibc` is built using maven. Run `mvn package` and the built target you'll want to use will be at `target/jlibc-snapshot-jar-with-dependencies.jar`
