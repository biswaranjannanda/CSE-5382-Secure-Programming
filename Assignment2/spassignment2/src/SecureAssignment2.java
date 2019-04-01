/*
Submitted By: Biswa Ranjan Nanda
Mav ID - 1001558251

References:
1. https://beginnersbook.com/2013/12/treemap-in-java-with-example/
2. https://math.hws.edu/eck/cs124/javanotes6/source/PhoneDirectoryFileDemo.java
3. http://stackoverflow.com/questions/42730785/java-regex-phone-number-validation
4. https://www.tutorialspoint.com/java/java_regular_expressions.htm
5. https://regexper.com/
 */

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Map;
import java.util.Scanner;
import java.util.TreeMap;

public class SecureAssignment2 {

    private static String fileName = "phonedata.csv";
    private static  Scanner in;

    public static void main(String[] args) {

        String name, phoneNumber;
        TreeMap<String, String> phoneBook = new TreeMap<String, String>();

        File saveDataFile = saveFile();

        if (!saveDataFile.exists()) {
            System.out.println("Phonebook file not found.\nAdd entries to create a new Phonebook File.\nFile location and file name:" + saveDataFile.getAbsolutePath());
        } else{
            System.out.println("Phone directory already exists:");
            try (Scanner scanner = new Scanner(saveDataFile)) {
                while (scanner.hasNextLine()) {
                    String newEntry = scanner.nextLine();
                    int separator = newEntry.indexOf('%');
                    if (separator == -1)
                        throw new IOException("File is not a phonebook data file.");
                    name = newEntry.substring(0, separator);
                    phoneNumber = newEntry.substring(separator + 1);
                    phoneBook.put(name, phoneNumber);
                }
            } catch (IOException e) {
                System.out.println("Error in Phone book file");
                System.out.println("File location and file name:  " + saveDataFile.getAbsolutePath());
                System.out.println("Error in program, so exits");
                System.exit(1);
            }
        }

        in = new Scanner(System.in);
        boolean changed = false;

        while (true) {
            System.out.println("\nEnter HELP to understand how to input values");
            System.out.println("Or Choose command like (ADD, DELNAME, DELNUM, LIST, EXIT): ");
            String cmd = in.nextLine().trim();

            String[] arguments = cmd.split(" ");

            // Switch cases for performing the operations in the phonebook directory

            switch (arguments[0].toUpperCase()) {
                case "ADD":
                    try {
                        String personName = cmd.substring(index(cmd, "\"", 1) + 1, index(cmd, "\"", 2));
                        String telePhone = cmd.substring(index(cmd, "\"", 3) + 1, index(cmd, "\"", 4));

                        if (personName.matches(checkNameFomat()) && telePhone.matches(checkNumberFormat())) {
                            System.out.println("Your entry has been added in the directory");
                            phoneBook.put(personName, telePhone);
                            changed = true;
                        } else {
                            System.out.println("Incorrect format of name/phone");
                        }
                    } catch (StringIndexOutOfBoundsException e) {
                        System.exit(1);
                    }
                    break;

                //Delete an entry with telephone number

                case "DELNUM":
                    String argumment = cmd.substring(index(cmd, "\"", 1) + 1, index(cmd, "\"", 2));
                    argumment = argumment.replace("\"", "");
                    String deleteNum = argumment.trim();
                    boolean boolTel = phoneBook.values().remove(deleteNum);
                    if (boolTel) {
                        changed = true;
                        System.out.println("\nDirectory entry is removed for " + deleteNum);
                    } else {
                        System.out.println("\nNo entry for " + deleteNum + "is available");
                    }
                    break;

                //Delete an entry with name

                case "DELNAME":
                    String argument = cmd.substring(index(cmd, "\"", 1) + 1, index(cmd, "\"", 2));
                    argumment = argument.replace("\"", "");

                    String personNameToDelete = argumment.trim();
                    String deleteName = phoneBook.get(personNameToDelete);
                    if (deleteName == null)
                        System.out.println("\nNo entry for " + personNameToDelete + "is available");
                    else {
                        phoneBook.remove(personNameToDelete);
                        changed = true;
                        System.out.println("\nDirectory entry is removed for " + personNameToDelete);
                    }
                    break;

                //List the phonebook directory

                case "LIST":
                    System.out.print("\n LIST CASE \n");
                    for (Map.Entry<String, String> entry : phoneBook.entrySet())
                        System.out.println("   " + entry.getKey() + ": " + entry.getValue());
                    break;

                //Help Option to understand how it works

                case "HELP":
                    System.out.println("********************---HELP OPTIONS---********************");
                    System.out.println("Add operation can be done using: ADD'<PERSON>'''<Phone #>'");
                    System.out.println("Delete a person in directory can be done using: DELNAME '<Name>'");
                    System.out.println("Delete a telephone number in directory can be done using:DELNUM '<Phone #>'");
                    System.out.println("List details of the PhoneBook directory: LIST");
                    break;

                case "EXIT":
                    System.exit(0);
                    break;

                default:
                    System.out.println("\nInvalid Option.");
                    System.exit(1);

            }

            if (changed) {
                changed = false;
                System.out.println("Changes being saved in the directory " +
                        saveDataFile.getAbsolutePath() + " ...");
                PrintWriter out;
                try {
                    out = new PrintWriter(new FileWriter(saveDataFile));
                } catch (IOException e) {
                    System.out.println("Error opening file");
                    return;
                }
                for (Map.Entry<String, String> entry : phoneBook.entrySet())
                    out.println(entry.getKey() + "%" + entry.getValue());
                out.flush();
                out.close();
                if (out.checkError())
                    System.out.println("Error occurred while reading the file");
                else
                    System.out.println("Done.");
            }
        }
    }

    private static int index(String str,String subStr, int n) {
        int position = str.indexOf(subStr);
        while(--n > 0 && position != -1)
            position = str.indexOf(subStr,position + 1);
        return position;
    }

    private static  String  checkNameFomat() {
        String nameFormat =  "([a-zA-Z]?\\'?([a-zA-Z]*\\, [a-zA-Z]* [a-zA-Z]*\\.?)|([a-zA-Z]+ [a-zA-Z][a-zA-Z]+)|([a-zA-Z]*, [a-zA-Z]*)|([a-zA-Z]*)|([a-zA-Z]* [a-zA-Z]'[a-zA-Z]*-[a-zA-Z]*))";
        return nameFormat;
    }

    private static String checkNumberFormat() {
        String numberFormat = "(\\d{5}.?\\d*|(\\d?\\(\\d{3}\\)\\d{3}-\\d{4})|(\\d{3}-\\d{4})|(\\+\\d{0,2} ?\\(\\d{2,3}\\) ?\\d{3}-\\d{4})|(\\d{3} \\d{3} \\d{3} \\d{4})|(\\+\\d{2} \\(\\d{2}\\) )|(\\d{3} \\d{1} \\d{3} \\d{3} \\d{4}))";
        return numberFormat;
    }

    private static File saveFile() {
        File homeDirectory = new File(System.getProperty("user.home"));
        File saveDataFile = new File(homeDirectory, fileName);
        return saveDataFile;
    }
}
