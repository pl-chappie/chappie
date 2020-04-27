/* ************************************************************************************************
* Copyright 2017 SUNY Binghamton
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

package jlibc.proc;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.ArrayList;
import java.util.HashMap;

import jlibc.libc;

public class Task {
  private int id;
  private String stat;
  private long timestamp;

  private Task(int id) throws IOException {
    this.id = id;

    String stat_file = "/proc/" + libc.getProcessId() + "/task/" + id + "/stat";
    if (Files.notExists(Paths.get(stat_file)))
      throw new IOException("process " + id + " could not be sampled");

    stat = Files.readString(Paths.get(stat_file));
    timestamp = System.currentTimeMillis();
  }

  // linux's task states; no reason not to make this explicit and accessible
  public enum State {RUNNABLE, INTERRUPTIBLE, UNINTERRUPTIBLE, ZOMBIE, TERMINATED, UNDEFINED}
  private static Task.State parseState(String state) {
    if (state.equals("R"))
      return State.RUNNABLE;
    else if (state.equals("S"))
      return State.INTERRUPTIBLE;
    else if (state.equals("D"))
      return State.UNINTERRUPTIBLE;
    else if (state.equals("Z"))
      return State.ZOMBIE;
    else if (state.equals("T"))
      return State.TERMINATED;
    else
      return State.UNDEFINED;
  }

  // stat fields we currently use; this could be extended further
  private int cpu;
  private State state;
  private long user_jiffies;
  private long kernel_jiffies;

  private static HashMap<Integer, String> task_names = new HashMap<Integer, String>();
  private Task parse() {
    // check if we've parsed this record;
    // we should have throw if it was read as null
    if (stat != null) {
      // since java uses spaces in thread names,
      // we can't just split on space (the stat delimiter).
      // we count the number of items, it should be 52;
      // any excess is the offset
      String[] stats = stat.split(" ");
      int offset = stats.length - 52;

      if (!task_names.containsKey(id)) {
        // I'm clipping the parens around thread
        String name = String.join(" ", Arrays.copyOfRange(stats, 1, 2 + offset));
        name = name.substring(1, name.length() - 1);
        task_names.put(id, name);
      }

      cpu = Integer.parseInt(stats[38 + offset]);
      state = Task.parseState(stats[2 + offset]);
      user_jiffies = Long.parseLong(stats[13 + offset]);
      kernel_jiffies = Long.parseLong(stats[14 + offset]);

      stat = null;
    }

    return this;
  }

  // getter boilerplate :(
  public int getId() { parse(); return id; }
  public int getCPU() { parse(); return cpu; }
  public State getState() { parse(); return state; }
  public long getUserJiffies() { parse(); return user_jiffies; }
  public long getKernelJiffies() { parse(); return kernel_jiffies; }

  @Override
  public String toString() {
    parse();

    return task_names.get(id) + "(" + id + ")@" + timestamp + ":\n - " +
      state.name() + "\n - " +
      "cpu: " + cpu + "\n - " +
      "user: " + user_jiffies + ", kernel: " + kernel_jiffies;
  }

  public Task[] getTasks() {
    File[] task_list = new File("/proc/" + libc.getProcessId() + "/task").listFiles();
    ArrayList<Task> tasks = new ArrayList<Task>(task_list.length);
    for (int i = 0; i < task_list.length; i++) {
      int tid = Integer.parseInt(task_list[i].getName());
      try { tasks.add(new Task(tid)); } catch (IOException e) { }
    }

    return tasks.toArray(new Task[tasks.size()]);
  }

  public static Task getTask(Thread thread) {
    try {
      return new Task(libc.getTaskId(thread));
    } catch(IOException e) {
      return null;
    }
  }

  public static Task currentTask() { return getTask(Thread.currentThread()); }

  public static Task mainTask() {
    try {
      return new Task(libc.getProcessId());
    } catch(IOException e) {
      return null;
    }
  }

  public static Task[] getCurrentTasks() {
    try {
      return mainTask().getTasks();
    } catch(NullPointerException e) {
      return new Task[0];
    }
  }

  public static HashMap<Long, Integer> getTaskIds() {
    return libc.getTIDs();
  }

  public static HashMap<Long, String> getTaskNames() {
    return (HashMap<Long, String>)task_names.clone();
  }
}
