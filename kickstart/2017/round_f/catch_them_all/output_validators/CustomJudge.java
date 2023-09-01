import java.io.File;
import java.util.Scanner;

public class CustomJudge {
  static final double EPSILON = 1e-4;

  public static void main(String[] args) throws Throwable {
    judge(args[0], args[1], args[2]);
  }

  static void judge(String inputFile, String outputFile, String answerFile) throws Throwable {
    Scanner outputSc = new Scanner(new File(outputFile));
    Scanner answerSc = new Scanner(new File(answerFile));

    while (true) {
      if (outputSc.hasNext() != answerSc.hasNext()) {
        throw new RuntimeException();
      }
      if (!outputSc.hasNext()) {
        break;
      }

      String outputToken = outputSc.next();
      String answerToken = answerSc.next();
      if (isDouble(outputToken) != isDouble(answerToken)) {
        throw new RuntimeException();
      }
      if (isDouble(outputToken)) {
        double outputValue = Double.parseDouble(outputToken);
        double answerValue = Double.parseDouble(answerToken);
        if (!(Math.abs(outputValue - answerValue) <= EPSILON
            || (answerValue != 0
                && Math.abs((outputValue - answerValue) / answerValue) <= EPSILON))) {
          throw new RuntimeException();
        }
      } else if (!outputToken.equals(answerToken)) {
        throw new RuntimeException();
      }
    }

    answerSc.close();
    outputSc.close();
  }

  static boolean isDouble(String s) {
    try {
      Double.parseDouble(s);

      return true;
    } catch (NumberFormatException e) {
      return false;
    }
  }
}
