import java.io.File;
import java.util.Scanner;
import java.util.function.BiConsumer;

public class JudgeUtil {
  public static void matchForSpace(String inputFile, String outputFile, String answerFile)
      throws Throwable {
    match(
        inputFile,
        outputFile,
        answerFile,
        (outputToken, answerToken) -> {
          if (!outputToken.equals(answerToken)) {
            throw new RuntimeException();
          }
        });
  }

  public static void matchForDouble(
      String inputFile, String outputFile, String answerFile, double epsilon) throws Throwable {
    match(
        inputFile,
        outputFile,
        answerFile,
        (outputToken, answerToken) -> {
          if (isDouble(outputToken) != isDouble(answerToken)) {
            throw new RuntimeException();
          }
          if (isDouble(outputToken)) {
            double outputValue = Double.parseDouble(outputToken);
            double answerValue = Double.parseDouble(answerToken);
            if (!(Math.abs(outputValue - answerValue) <= epsilon
                || (answerValue != 0
                    && Math.abs((outputValue - answerValue) / answerValue) <= epsilon))) {
              throw new RuntimeException();
            }
          } else if (!outputToken.equals(answerToken)) {
            throw new RuntimeException();
          }
        });
  }

  static boolean isDouble(String s) {
    try {
      Double.parseDouble(s);

      return true;
    } catch (NumberFormatException e) {
      return false;
    }
  }

  static void match(
      String inputFile,
      String outputFile,
      String answerFile,
      BiConsumer<String, String> tokenMatcher)
      throws Throwable {
    try (Scanner outputSc = new Scanner(new File(outputFile));
        Scanner answerSc = new Scanner(new File(answerFile))) {
      while (true) {
        if (outputSc.hasNext() != answerSc.hasNext()) {
          throw new RuntimeException();
        }
        if (!outputSc.hasNext()) {
          break;
        }

        String outputToken = outputSc.next();
        String answerToken = answerSc.next();
        tokenMatcher.accept(outputToken, answerToken);
      }
    }
  }
}