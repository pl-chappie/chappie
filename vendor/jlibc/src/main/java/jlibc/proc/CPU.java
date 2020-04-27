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
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;

public class CPU {
  private String stat;
  private int freq;
  private long timestamp;

  private CPU(String stat, int freq) {
    this.stat = stat;
    this.freq = freq;
    timestamp = System.currentTimeMillis();
  }

  private int cpu;

  // jiffies
  private long user;
  private long nice;
  private long kernel;
  private long idle;
  private long iowait;
  private long irq;
  private long softirq;
  private long steal;
  private long guest;
  private long guest_nice;

  private CPU parse() {
    if (stat != null) {
      String[] stats = this.stat.split(" ");
      stats[0] = stats[0].substring(3, stats[0].length());

      cpu = Integer.parseInt(stats[0]);
      user = Long.parseLong(stats[1]);
      nice = Long.parseLong(stats[2]);
      kernel = Long.parseLong(stats[3]);
      idle = Long.parseLong(stats[4]);
      iowait = Long.parseLong(stats[5]);
      irq = Long.parseLong(stats[6]);
      softirq = Long.parseLong(stats[7]);
      steal = Long.parseLong(stats[8]);
      guest = Long.parseLong(stats[9]);
      guest_nice = Long.parseLong(stats[10]);

      stat = null;
    }

    return this;
  }

  // getter boilerplate :(
  public int getCPU() { parse(); return cpu; }
  public long getUserJiffies() { parse(); return user; }
  public long getNiceJiffies() { parse(); return nice; }
  public long getKernelJiffies() { parse(); return kernel; }
  public long getIdleJiffies() { parse(); return idle; }
  public long getIOWaitJiffies() { parse(); return iowait; }
  public long getIRQJiffies() { parse(); return irq; }
  public long getSoftIRQJiffies() { parse(); return softirq; }
  public long getStealJiffies() { parse(); return steal; }
  public long getGuestJiffies() { parse(); return guest; }
  public long getGuestNiceJiffies() { parse(); return guest_nice; }
  public long getFreq() { parse(); return freq; }

  @Override
  public String toString() {
    parse();

    return "CPU " + cpu + "\n - " +
      "freq: " + freq + "\n - " +
      "user: " + user + "\n - " +
      "kernel: " + kernel + "\n - " +
      "nice: " + nice + "\n - " +
      "idle: " + idle + "\n - " +
      "iowait: " + iowait + "\n - " +
      "irq: " + irq + "\n - " +
      "softirq: " + softirq + "\n - " +
      "steal: " + steal + "\n - " +
      "guest: " + guest + "\n - " +
      "guest_nice: " + guest_nice;
  }

  private static int cpu_count = Runtime.getRuntime().availableProcessors();
  private static CPU[] cpus = new CPU[cpu_count];

  private static HashMap<Integer, Integer> max_freqs = new HashMap<Integer, Integer>();
  public static CPU[] getCPUs() {
    try {
      String[] stats = Files.readString(Paths.get("/proc/stat")).split("\n");

      for (int i = 0; i < cpu_count; i++) {
        if (!max_freqs.containsKey(i)) {
          // I'm clipping the parens around thread
          int max_freq = Integer.parseInt(Files.readString(Paths.get(
            "/sys/devices/system/cpu/cpu" + Integer.toString(i) + "/cpufreq/cpuinfo_max_freq")).split("\n")[0]);
          max_freqs.put(i, max_freq);
        }
        int freq = Integer.parseInt(Files.readString(Paths.get(
          "/sys/devices/system/cpu/cpu" + Integer.toString(i) + "/cpufreq/cpuinfo_cur_freq")).split("\n")[0]);
        cpus[i] = new CPU(stats[i + 1], freq);
      }

      return cpus.clone();
    } catch (IOException e) {
      e.printStackTrace();
      return null;
    }
  }

  public static long getFreq(int cpu) {
    try {
      return Integer.parseInt(Files.readString(Paths.get(
        "/sys/devices/system/cpu/cpu" + Integer.toString(cpu) + "/cpufreq/cpuinfo_cur_freq")).split("\n")[0]);
    } catch (IOException e) {
      return -1;
    }
  }

  public static long[] getFreqs() {
    long[] freqs = new long[cpu_count];
    for (int i = 0; i < cpu_count; i++) {
      freqs[i] = getFreq(i);
    }

    return freqs;
  }

  public static CPU getCPU(int cpu) {
    if (cpus == null)
      getCPUs();

    return cpus[cpu];
  }

  public static HashMap<Integer, Integer> getMaxFreqs() {
    return (HashMap<Integer, Integer>)max_freqs.clone();
  }
}
