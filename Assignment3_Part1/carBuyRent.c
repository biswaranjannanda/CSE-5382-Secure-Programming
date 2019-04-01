#include <stdio.h>
#include <stdlib.h>
#include <string.h>

   // User Validation Function

int userValidate(char username[20], char password[16]){ 
   int flag = 0;
   char password_buffer[16];
   char username_buffer[20];

   strcpy(password_buffer, password);
   strcpy(username_buffer, username);

   if((strcmp(password, "password") == 0) && (strcmp(username, "admin") == 0))
      flag = 1;

   return flag;
}
   
   // Function to calculate the price for Car rental

double rentCar(int car, int days){  
      double rate = 0;
      if(car==1)
         rate = days * 90;
      else if(car==2)
         rate = days * 60;
      else if(car==3)
         rate = days * 40;
      else if(car==4)
         rate = days * 400;
      else
         printf("Invalid option, choose the correct option.");

      return rate;
   }

   // Function to calculate the price for Car purchase

double buyCar(int car){
      double rate = 0;

      if(car==1)
         rate = 40000;
      else if(car==2)
         rate = 35000;
      else if(car==3)
         rate = 20000;
      else if(car==4)
         rate = 65000;
      else
         printf("Invalid option, choose the correct option.");

      return rate;
   }

int main(){
   char username[20];
   char password[16];
   char car_Buy_or_Rent;
   int car;
   char car_name[30];
   int days;
   double rate;
   printf("\n\t\tCar Buy or Rental System\n");
   printf("\n*********************************************************");
   printf("\nEnter Customer username: ");
   scanf("%s", &username);
   printf("\nEnter your password: ");
   scanf("%s", &password);

   if(userValidate(username, password))
   {
      printf("\nLogin successfull, Please proceed further.");
      printf("\n*******************************************");
      
      printf("\n\nEnter Type:\n'B' to purchase car \n'R' to rent car\n ");
      scanf(" %c",&car_Buy_or_Rent);
      printf("\n\n1. 7 Seater Car\n2. 5 Seater Car\n3. 4 Seater Car\n4. 2 Seater Car\nEnter #number for the Car Type: ");
      scanf("%d", &car);
      printf("\nEnter car name: ");
      scanf("%s", &car_name);
      if(car_Buy_or_Rent == 'R'){
         printf("Enter # of days for renting: ");
         scanf("%d", &days);
      }

      if(car_Buy_or_Rent == 'B' || car_Buy_or_Rent == 'b')
         rate = buyCar(car);
      else if(car_Buy_or_Rent == 'R' || car_Buy_or_Rent == 'r')
         rate = rentCar(car,days);


      printf("\n\n\n\t\t\tConfirmation\n");
      printf("\nHello %s", username);
      printf("\n\nTotal Amount: $%.2f", rate);
      if(car_Buy_or_Rent == 'B' || car_Buy_or_Rent == 'b'){
         printf("\nCar %s is Purchased successfully.\n", car_name);
      }
      else if(car_Buy_or_Rent == 'R' || car_Buy_or_Rent == 'r'){
         printf("\nCar %s is Rented successfully for %d days.\n", car_name, days);
      }
   }
   else{
      printf("\n*********************************************");
      printf("\nPlease Enter CORRECT username and password!! ");
      printf("\n*********************************************\n");
   }

   
}

