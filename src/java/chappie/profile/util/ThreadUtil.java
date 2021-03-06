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

package chappie.profile.util;

import chappie.util.ChappieLogger;

import java.util.concurrent.locks.LockSupport;

public class ThreadUtil {
  // the code to do this is messy so it's just easier to tuck it here in case
  // we need this again
  public static void sleepUntil(long start, long end) throws InterruptedException {
    long elapsed = System.nanoTime() - start;
    long millis = elapsed / 1000000;
    int nanos = (int)(elapsed - millis * 1000000);

    millis = end - millis - (nanos > 0 ? 1 : 0);
    nanos = Math.min(1000000 - nanos, 999999);

    if (millis >= 0 && nanos > 0)
      Thread.sleep(millis, nanos);
  }

  public static void sleepUntilNanos(long start, long end) throws InterruptedException {
    long elapsed = System.nanoTime() - start;
    long millis = elapsed / 1000000;
    int nanos = (int)(elapsed - millis * 1000000);

    if (millis <= 0) {
      nanos = (int)end - nanos;
      LockSupport.parkNanos(nanos - 80000);
    }
    // ChappieLogger.getLogger().info("total: " + (System.nanoTime() - start));
  }
}
