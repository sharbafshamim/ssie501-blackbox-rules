
# Libraries used in code
import random

#--------------------------------Entry Screen-------------------------------------------
sim_step_start = 0
start = input ("Enter 1 to start or 0 to exit")

if start != "1":
    print ("Well that's no fun! Please exit the program")
    
else:
    print ("Current Step:", sim_step_start) #prints the current step on the screen

#-------------------------------Prints Initial Matrix---------------------------------
# Sets up 10x10 grid with random numbers 0,9, divided into 4 equal, 5x5 regions

Region = 5 #sets number of columns and rows in each region

tableR1 = [
    [random.randint(0, 9) for _ in range(Region)] #generates a random number
    for _ in range(Region)
]

tableR2 = [
    [random.randint(0, 9) for _ in range(Region)]
    for _ in range(Region)
]

tableR3 = [
    [random.randint(0, 9) for _ in range(Region)]
    for _ in range(Region)
]

tableR4 = [
    [random.randint(0, 9) for _ in range(Region)]
    for _ in range(Region)
]

# Instructions on how to display the matrix with the regions blocked off to make them more visible
def display_table():
   print("        Region 1             Region 2")
   for row1, row2 in zip(tableR1, tableR2):
        left = " ".join(f"{value:3}" for value in row1)
        right = " ".join(f"{value:3}" for value in row2)
        print(f"{left}  | {right}")
   print(" -----------------------------------------")

   for row3, row4 in zip(tableR3, tableR4):
        left = " ".join(f"{value:3}" for value in row3)
        right = " ".join(f"{value:3}" for value in row4)
        print(f"{left}  | {right}")
   print("        Region 3             Region 4")
      
display_table() # this line tells the computer to show the matrix on the screen

#------------------------------ User Entry: n value & command --------------------------------------

# These lines request the user to provide answers that control the model

n = int(input(" n =")) # how many steps do you want to run at one time
print ("\nn = ", n)

command = input("\nEnter Command: 1 = Complete ""n"" steps") # run the number of steps entered

sim_step = 0 # The model always starts at Step 0 = random, this will print on the screen later

#-------------------------------Generate Random Matrix------------------------------------------

# This section pics a random cell for each reagion by identifying a random number 1-5,
# for the Row (x) and column (y) coordinates to form (x,y) shown as table[x][y]

def update_matrix():  
    rowR1 = random.randrange(len(tableR1))
    colR1 = random.randrange(len(tableR1[rowR1]))

    rowR2 = random.randrange(len(tableR2))
    colR2 = random.randrange(len(tableR2[rowR2]))

    rowR3 = random.randrange(len(tableR3))
    colR3 = random.randrange(len(tableR3[rowR3]))

    rowR4a = random.randrange(len(tableR4))
    colR4a = random.randrange(len(tableR4[rowR4a]))
    
    rowR4b = random.randrange(len(tableR4))
    colR4b = random.randrange(len(tableR4[rowR4b]))

#---------------------Identify Values of Selected Cells & Reference Cells--------------------
    
    # Assign variables (psuedonyms) for the value of the randomly selected cell, makes it easier to reference later
    R1_old = tableR1[rowR1][colR1]
    R2_old = tableR2[rowR2][colR2]
    R3_old = tableR3[rowR3][colR3]
    R4a_old = tableR4[rowR4a][colR4a]
    R4b_old = tableR4[rowR4b][colR4b]
        
                    
    # Identifies a speciic cell in each of the other regions that can be used in update calculations
    # in the actual BlackBox, each cell has a dedicated refernce in another region, here we simplify to 1
    # per region to show the mechanism in a simpler model.
    rowR1r = 2
    colR1r = 2
    R1_ref = tableR1[rowR1r][colR1r] # This is the center cell in Region 1
    
    rowR2r = 2
    colR2r = 2
    R2_ref = tableR2[rowR2r][colR2r] # This is the center cell in Region 2

    rowR3r = 2
    colR3r = 2
    R3_ref = tableR3[rowR3r][colR3r] # This is the center cell in Region 3

    # Region 4 uses two random cells to serve as a reference. If the cell next to it is the same as the one
    # chosen at random, this is a positive sign Region 4 is progressing to its end point.
    rowR4ra = random.randrange(len(tableR4))
    colR4ra = random.randrange(len(tableR4[rowR4a]))
    R4_refa = tableR4[rowR4ra][colR4ra] 
    
    R4_refb = tableR4[rowR4ra][colR4ra-1] 
    
#-----------------------------Display Intermediate Variables------------------------------------------------------------
    # Displays the value of the reference cells defined above & the value of the cell that
    # was selected to change and reprints the tables with the new value after rules have run
    # these steps would not normally be "printed" they are included so you can see what the model is 
    # doing "behind the scenes"
    
    print('\nValue of Reference Cells:',
          "\n   Region 2:", R2_ref,
          "\n   Region 3:", R3_ref,
          "\n   Region 4:", R4_refa, "&", R4_refb)
    

    print("\nValue of Cell Picked in each Region:",
          "\n   Region 1:", (f"R{rowR1 + 1}C{colR1 + 1} ="), R1_old,
          "\n   Region 2:", (f"R{rowR2 + 1}C{colR2 + 1} ="), R2_old,
          "\n   Region 3:", (f"R{rowR3 + 1}C{colR3 + 1} ="), R3_old,
          "\n   Region 4:", (f"R{rowR4a + 1}C{colR4a + 1} ="), R4a_old, "&", (f"R{rowR4b + 1}C{colR4b + 1} ="), R4b_old)
    
#-----------------------------REGION 1 UPDATE RULE---------------------------------------------------------------------      
    
    # Sets the rule for the cell in Region 1 to follow for updates, in the real black box, there is a formula
    # for each cell, in ours we have used the same formula for the entire region to demonstrate the rule.
   
        
    def R1_rule():
        print ("\nRegion 1 Variables & Activity:") 
        if R1_old == 4 or R1_old == 5:			#if the cell value is 4 or 5, no change
            tableR1[rowR1][colR1] = R1_old
                
        elif R1_old > 5:						
            tableR1[rowR1][colR1] = R1_old - 1	#if the cell value is greater than 5, subtract 1
                
        elif R1_old < 4:
            tableR1[rowR1][colR1] = R1_old + 1	#if the cell value is less than 4, add 1
               
        if R1_old <4:
           print (f"   R{rowR1 + 1}C{colR1 + 1} is less than 4, +1")
        elif R1_old >5:
           print (f"   R{rowR1 + 1}C{colR1 + 1} is greater than 5, -1")
        elif R1_old == 4 or R1_old == 5:
           print (f"   R{rowR1 + 1}C{colR1 + 1} is", R1_old, ", No change")
           
        
    R1_rule() #runs the rule and updates the selected cell in the Region 1 table

#-----------------------------REGION 2 UPDATE RULE-----------------------------------------------------------------------
    
    # Sets the rule for the cell in Region 2 to follow for updates, this region follows the example of an
    # evolving system as described in Ashby, W. R. (1991). Principles of the Self-Organizing System. "Competition" 
    # In G. J. Klir, Facets of Systems Science (pp. 521–536). Springer US. https://doi.org/10.1007/978-1-4899-0718-9_38
    
    def R2_rule():
        print ("\nRegion 2 Variables & Activity:")
        
        # If the value is 2 digits, the rule only keeps the right one. Example: if 12, would be 2
        # Multiplys the chosen cell by the one prior to it in the row. 
        
        if tableR2[colR2] != 0: #checks if the cell selected is in column 6 in the matrix
            Add_to_R3 = R2_old * tableR2[rowR2][colR2-1]
            tableR2[rowR2][colR2] = (R2_old * tableR2[rowR2][colR2-1]) % 10 
            print (f"   R{rowR2 + 1}C{colR2 + 1} =", R2_old)
            print (f"   R{rowR2 + 1}C{colR2} =", tableR2[rowR2][colR2-1])
            print ("  ", R2_old, "x", tableR2[rowR2][colR2-1], "=", Add_to_R3)
            print ("   New Value =", tableR2[rowR2][colR2])
        
        else: # if the cell IS in column 6, it pulls from the last colmn in Region 1  
           Add_to_R3 = R2_old * tableR1[0][4]
                                           
           tableR2[rowR2][colR2] = (R2_old * tableR1[rowR2][4]) % 10 
           print (f"   R{rowR2 + 1}C{colR2 + 1} =", R2_old)
           print (f"   R{rowR2 + 1}C{colR2} =", tableR2[row2][colR2-1])
           print ("  ", R2_old, "x", tableR1[rowR2][4], "=", Add_to_R3)
           print ("   New Value =", tableR2[rowR2][colR2])
            
    R2_rule() #runs the rule and updates the selected cell in the Region 2 table
    

#------------------------------REGION 4 UPDATE RULE------------------------------------------------------------------------------------------------------------
    def R4_rule():
        print ("\nRegion 4 Variables & Activity:")
        # variables (placeholder) for counting if neighbors are the same as the random selected cells
        n_count_a = 0
        n_count_b = 0
        
               
 #Validate cell values and accept or reject swap

        print ("   Cell '"'a'"' Value = ", R4a_old), 
        neighbors_a = []

        # Left: use Region 3's last column at the left edge of Region 4
        if colR4a == 0:
            neighbors_a.append(tableR3[rowR4a][4])
        else:
            neighbors_a.append(tableR4[rowR4a][colR4a - 1])

        # Right: neighboring cell within Region 4
        if colR4a < 4:
            neighbors_a.append(tableR4[rowR4a][colR4a + 1])

        # Up: use Region 2's last row at the top edge of Region 4
        if rowR4a == 0:
             neighbors_a.append(tableR2[4][colR4a])
        else:
             neighbors_a.append(tableR4[rowR4a - 1][colR4a])

        # Down: neighboring cell within Region 4
        if rowR4a < 4:
             neighbors_a.append(tableR4[rowR4a + 1][colR4a])       
        print ("   Neighbors of '"'a'"' =", neighbors_a)
        for value in neighbors_a:
             if value == R4b_old:
                    n_count_b +=1
        

            
        print ("\n   Cell '"'b'"' Value = ", R4b_old)         
        
        neighbors_b = []

        # Left: use Region 3's last column at the left edge of Region 4
        if colR4b == 0:
            neighbors_b.append(tableR3[rowR4b][4])
        else:
            neighbors_b.append(tableR4[rowR4b][colR4b - 1])

        # Right: neighboring cell within Region 4
        if colR4b < 4:
            neighbors_b.append(tableR4[rowR4b][colR4b + 1])

        # Up: use Region 2's last row at the top edge of Region 4
        if rowR4b == 0:
             neighbors_b.append(tableR2[4][colR4b])
        else:
             neighbors_b.append(tableR4[rowR4b - 1][colR4b])

        # Down: neighboring cell within Region 4
        if rowR4b < 4:
             neighbors_b.append(tableR4[rowR4b + 1][colR4b])       
        print ("   Neighbors of b =", neighbors_b)
        for value in neighbors_b:
             if value == R4a_old:
                    n_count_a +=1
        print ("\n   Number of '"'a'"' neighbors that match '"'b'"' = ", n_count_a)
        print ("   Number of '"'b'"' neighbors that match '"'a'"' = ", n_count_b)


        
            
        if n_count_a > 0 or n_count_b > 0:
            tableR4[rowR4a][colR4a] = R4b_old
            tableR4[rowR4b][colR4b] = R4a_old
        else:
            tableR4[rowR4a][colR4a] = R4a_old
            tableR4[rowR4b][colR4b] = R4b_old 
    
    R4_rule()

#----------------------------REGION 3 UPDATE RULE---------------------------------------------------------------------------

    # Updates the cell with a value selected based on probability, references the cells in other regions
    # If they are reaching their end point the region will settle into a continuous cycle. The proability
    # is based on observation of values in the original Black Box

    def R3_rule():
        print ("\nRegion 3 Variables & Activity:")
        global selected
        new_num = [7, 6, 5, 4, 3, 2, 1, 0]
        prob = [1, 1, 10, 10, 10, 33] # proability of being selected
       
        pick_num = random.random() * sum(prob) # Picks a random point from 0-1.
        total = 0
        
        for new_num, weight in zip(new_num, prob):  # Check which value's probability range contains the random point.
            total += weight
            if pick_num < total:
                selected = new_num
                print ("    Value of selected cell = ",selected)
                print ("    Probability of new value: p = ",pick_num)
                break
                
     # Cross-ties with other Regions 
    
        if R1_ref == (4 or 5) and R2_ref == 0 and R3_ref <= 3 and (R4a_ref == R4b_ref): # if R1-R4 are in steady state, update cell based on p=
             tableR3[rowR3][colR3] = selected
             print ("   updated to =", tableR3[rowR3][colR3])
                    
        elif R1_ref == (4 or 5) and R2_ref == 0 and R3_ref <= 3 and (R4a_ref != R4b_ref): #if R1-R3 are in steady state and R4 don't match, add the value of the selected cell and the reference cell
             tableR3[rowR3][colR3] = R3_ref + selected
             print ("   updated to =", tableR3[rowR3][colR3])
        else:
            tableR3[rowR3][colR3] = random.randint(0, 9) # if none of the regions are settled, the cell updates to a random value 0-9
            print ("    updated to =", tableR3[rowR3][colR3])                 
                       
    R3_rule()

          
    print("\nNew Value of Cell Picked in each Region:",
          "\n   Region 1:", (f"R{rowR1 + 1}C{colR1 + 1} ="), (f"{tableR1[rowR1][colR1]}"),
          "\n   Region 2:", (f"R{rowR2 + 1}C{colR2 + 1} ="), (f"{tableR2[rowR2][colR2]}"),
          "\n   Region 3:", (f"R{rowR3 + 1}C{colR3 + 1} ="), (f"{tableR3[rowR3][colR3]}"),
          "\n   Region 4:", (f"R{rowR4a + 1}C{colR4a + 1} ="), (f"{tableR4[rowR4a][colR4a]}"), "&", (f"R{rowR4b + 1}C{colR4b + 1} ="), (f"{tableR4[rowR4b][colR4b]}") )
    
def run():
    global sim_step
    if command == "0": # if command = 0, tables are reset to random
        print("Reset Table") #displays the new random table
        display_table()
        
    elif command == "1": #selects a cell based on rules for each region and updates
        global n
        for _ in range(n): #repeats the update_matrix code for "n" times based on user entry
            print (" ________________\n") 
            sim_step = sim_step +1 
            print ("\nUpdate Step:", sim_step)
            update_matrix() #runs the code that updats the tables
            print ("\nNew Table:")
            
            display_table()
                              
run()

def run_again(): 
     global n
     ask_me = int(input("\nDo you want to run again? 0 = No, 1 = Yes"))
     if ask_me == 0:
             print ("Well that's no fun! Please exit the program")
     else:
        n = int(input(" n ="))
        print ("\nn = ", n)
        command = input("\nEnter Command: 0 = Reset, 1 = Advance")
        run()
        run_again()

run_again()
              
              