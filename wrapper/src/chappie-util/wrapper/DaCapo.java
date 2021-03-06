package chappie_util.wrapper;

import chappie.Chaperone;

import org.dacapo.harness.Callback;
import org.dacapo.harness.CommandLineArgs;

public class DaCapo extends Callback {
  Chaperone chappie;

  public DaCapo(CommandLineArgs args) { super(args); }

  @Override
  public void start(String benchmark) {
    chappie = new Chaperone();
    chappie.start();
    super.start(benchmark);
  }

  @Override
  public void stop(long duration) {
    super.stop(duration);
    chappie.stop();
  }
}
