import java.io.File;
import java.util.Scanner;

public class CustomJudge {
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
      if (!outputToken.equals(answerToken)) {
        throw new RuntimeException();
      }
    }

    answerSc.close();
    outputSc.close();
  }
}
