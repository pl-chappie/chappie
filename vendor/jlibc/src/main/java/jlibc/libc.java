/* ************************************************************************************************
* Copyright 2019 SUNY Binghamton
* Permission is hereby granted, free of charge, to any person obtaining a copy of this
* software and associated documentation files (the "Software"), to deal in the Software
* without restriction, including without limitation the rights to use, copy, modify, merge,
* publish, distribute, sublicense, and/or sell copies of the Software, and to permit
* persons to whom the Software is furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in all copies or
* substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
* INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
* PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
* FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
* OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
* DEALINGS IN THE SOFTWARE.
* ***********************************************************************************************/

package jlibc;

import java.io.IOException;
import java.util.HashMap;

import com.sun.jna.Library;
import com.sun.jna.Native;

interface libcl extends Library {
  static libcl instance = (libcl)Native.loadLibrary("c", libcl.class);

  int getpid();
  int gettid();

  int syscall(int id, Object ... args);
}

public abstract class libc {
  // pid methods
  // flags to check for implementation
  private static boolean no_getpid = false;
  private static boolean no_pid_syscall = false;

  public static int getpid() {
    if (!no_getpid) {
      try {
        return libcl.instance.getpid();
      } catch (UnsatisfiedLinkError e) { no_getpid = true; }
    }

    if (!no_pid_syscall) {
      try {
        return libcl.instance.syscall(39);
      } catch (UnsatisfiedLinkError e) { no_pid_syscall = true; }
    }

    return -1;
  }

  // tid methods
  // flags to check for implementation
  private static boolean no_gettid = false;
  private static boolean no_tid_syscall = false;

  public static int gettid() {
    if (!no_gettid) {
      try {
        return libcl.instance.gettid();
      } catch (UnsatisfiedLinkError e) { no_gettid = true; }
    }

    if (!no_tid_syscall) {
      try {
        return libcl.instance.syscall(186);
      } catch (UnsatisfiedLinkError e) { no_tid_syscall = true; }
    }

    return -1;
  }

  // we cache the pid because it never changes
  private static Integer pid = getpid();
  public static int getProcessId() { return pid; }

  // we keep a local mapping of the jvm and os ids
  private static HashMap<Integer, Integer> thread_tids = new HashMap<Integer, Integer>();

  // this can only get the id of the calling thread
  // since that's unix gettid's implementation
  public static int getTaskId() {
    Thread current = Thread.currentThread();
    int id = (int)current.getId();

    if (!thread_tids.containsKey(id)) {
      int tid = gettid();
      if (tid > 0)
        thread_tids.put(id, tid);
    }

    return getTaskId(current);
  }

  // allows getting a tid from any process, assuming
  // it has been mapped (i.e. called getTaskId())
  public static int getTaskId(Thread thread) {
    int id = (int)thread.getId();

    if (thread_tids.containsKey(id))
      return thread_tids.get(id);
    else
      return -1;
  }

  // returns all tids that have been mapped, not all possible tids.
  public static HashMap<Long, Integer> getTIDs() {
    return (HashMap<Long, Integer>)thread_tids.clone();
  }
}
