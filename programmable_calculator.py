## A SIMPLE SCIENTIFIC CALCULATOR, LEVERING THE MATH CLASS,
## WITH UNLIMITED DEFINABLE VARIABLES, A RUNNING LOG OF ENTRIES

import math
from stack import Stack

class TraceStack(Stack):

     def __init__(self):

          self.limit = 1000
          self.stack = []

     def set_limit (self,limit):
          self.limit = limit


     def add (self,value):
          if len(self.stack)<self.limit:
               self.stack.append(value)
          else:
               self.stack.pop(0)
               self.stack.append(value)
     

class Register:

     """ Class for storing and accessing variables and constants"""

     def __init__ (self):

         self.variables = {}
         self.constants = {'pi':math.pi,
                           'e':math.e,
                           'tau':math.tau,
                           'inf':math.inf,
                           'nan':math.nan}

     def get (self, name):

          if name in self.variables:
               return self.variables[name]
          if name in self.constants:
               return self.constants[name]
     def set (self, name,value):
          if name not in self.constants:
               self.variables[name] = value

     def contains (self,name):
          return name in self.variables or name in self.constants

     

class Program:

     def __init__ (self):

          self.program_lines = []
          self.line_directory = {}
          self.program_blocks = {}
          self.reverse_blocks = {}
          self.variables = Register()
          self.calculator = Calculator(register=self.variables)
          self.logic = Logic(oracle = self)
          self.trace_stack = TraceStack()

     def contains (self,x):

          return x in self.variables.variables

     def get (self,x):
          

          COMPTERMS = ['==','>=','<=','!=','>','<',]
     

          def contains_comp (x):

               for comp in COMPTERMS:
                    if comp in x:
                         return True
               return False

          def comp_split (phrase):
               level = 0

               phrase = list(phrase)
               for index, x in enumerate(phrase):
                    if 'x' == '(':
                         level += 1
                    elif 'x' == ')':
                         level -= 1 
                    if level == 0:
                         found = False
                         for comp in COMPTERMS:
                              if len(comp) == 2 and x == comp[0] and phrase[index+1]==comp[1]:
                                   phrase[index] = '#'+comp[0]
                                   phrase[index+1] = comp[1]+'#'
                                   found = True 
                              
                              elif not found and len(comp) == 1 and x == comp:
  
                                   phrase[index] = '#'+x+'#'

               phrase = ''.join(phrase).split('#')

               newphrase = []
               for x in phrase:
                    if x in COMPTERMS:
                         newphrase.append(x)
                    else:
                         newphrase.append(self.calculator.calculate(x))
               return newphrase
          
          def evaluate_comp_list (phrase):

               def compare (a,R,b):


                    if R == '==':
                         return a==b
                    elif R == '!=':
                         return a!=b
                    elif R == '>':
                         return a>b
                    elif R == '<':
                         return a<b
                    elif R == '>=':
                         return a>=b
                    elif R == '<=':
                         return a<=b
               def get_triads (phrase):
                    triads = []
                    for count, x in enumerate(phrase):

                         if count % 2 == 0 and count+2 < len(phrase):
                              triads.append((phrase[count],phrase[count+1],phrase[count+2]))
                    return triads
               
               comp_results = []
               for x in get_triads(phrase):
                    if not compare(x[0],x[1],x[2]):
                         return False
               return True

          if x in self.variables.variables:
               val = self.variables.variables[x]


               return val
          else:

               if contains_comp(x):
                   
                    
                    phrase = comp_split(x)
                    if contains_comp(phrase):
                         return evaluate_comp_list(phrase)
                    else:
                         phrase = [self.logic.interpret(self.logic.parse(x)) for x in phrase]
                         for phr in phrase:
                              if not phr:
                                   return False
                              return True
               return None
                    
               
               


     def read_line (self,x):
          
          x = x.strip()
          if not x:
               return False, False, False, False
          x=list(x)
          lastspace = False
          spacecount = 0
          p_level = 0
          q_level = 0
          first_q = ''
          for index, char in enumerate(x):
               if char == '(':
                    p_level +=1
               if char == ')':
                    p_level -=1
               if char == "'" and not first_q:
                    q_level +=1
                    first_q = char 
               if char == "'" and first_q == "'":
                    q_level -=1
                    first_q = ''
               if char == '"' and not first_q:
                    q_level +=1
                    first_q = char
               if char == '"' and first_q =='"':
                    q_level -= 1
                    first_q = ''
                    
               if not lastspace and spacecount < 4 and char == ' ' and p_level == 0 and q_level == 0:
                    lastspace = True
                    spacecount +=1 
                    x[index] = '<#SPACING#>'
               elif lastspace and char == ' ':
                    pass
               elif char != ' ':
                    lastspace = False
          x = ''.join(x)

          x = x.split('<#SPACING#>')+[None, None, None]
          return int(x[0]), x[1], x[2], x[3]
          

     def load (self,script):

          def sis(x):
               if isinstance(x,str):
                    return x.strip()
               return x 

          for line in script.split('\n'):
               print(line)
               if line.strip() and line.strip()[0] == '#':
                    pass

               line_no, command, value1, value2 = self.read_line(line)
               if line_no:
                    index = len(self.program_lines)
                    self.line_directory[line_no] = index
                    
                    self.program_lines.append((command,
                                               sis(value1),
                                               sis(value2)))

     def find_blocks (self):

          indexes = Stack()
          for counter, line in enumerate(self.program_lines):

               if line[0] == 'WHILE':
                    indexes.add(counter)
               elif line[0] == 'ENDWHILE':
                    x = indexes.pop()
                    self.program_blocks [counter] = x
                    self.reverse_blocks [x] = counter 


     def run (self):


          self.trace_stack = TraceStack()
          line_counter = 0

          try:
          
          
               while line_counter < len(self.program_lines):

                    try:

                    

                         line = self.program_lines[line_counter]

                         line_counter += 1
                         command, value1, value2 = line[0], line[1], line[2]
                         if not value1 is None:
                              if value2 is None:
                                   terms = 1
                              else: terms = 2
                         else:
                              terms = 0
                         if value1 == '=':
                              command = command + value1 + value2
                         if '=' in command:

                              subject = command.split('=')[0]
                              predicate = self.calculator.calculate(command.split('=')[1])
                              self.variables.set(subject,predicate)
                         

                         elif command in ['IS',
                                        'GOTO',
                                        'WHILE',
                                        'ENDWHILE',
                                        'PRINT',
                                        'IFSKIP',
                                        'PRINTLINE']:
                              def debracket (x):
                                   if isinstance(x,str):
                                        if x[0]+x[-1] in ['""',"''"]:
                                             return x[1:-1]
                                   return x
                              if command == 'IS' and terms == 2:

                                   self.variables.set(value1,self.calculator.calculate(value2))
                                   self.trace_stack.add(str(line_counter)+' IS:'+value1)
                                   
                              elif command == 'GOTO':
                                   line_counter = self.line_directory[int(value1)]
                                   self.trace_stack.add(str(line_counter)+' GOTO:'+value1+'/'+str(line_counter))
                                   
                              elif command == 'WHILE':

                                   if not self.get(value1):
                                        line_counter = self.reverse_blocks[line_counter-1]+1
                                        self.trace_stack.add(str(line_counter)+' TERMINATES WHILE')
                                        self.trace_stack.add(str(line_counter)+' GOTO '+str(line_counter))
                                   self.trace_stack.add(str(line_counter)+' WHILE CONTINUES')
                              elif command == 'ENDWHILE':
                                   line_counter = self.program_blocks[line_counter-1]
                                   self.trace_stack.add(str(line_counter)+' WHILE RETURN')
                                   self.trace_stack.add(str(line_counter)+' GOTO '+str(line_counter))
                                   
                              elif command == 'IFSKIP':
                                   if self.get(value1):
                                        line_counter += 1
                                        self.trace_stack.add(str(line_counter)+' IFSKIP TRUE')
                                   self.trace_stack.add(str(line_counter)+' IFSKIP FALSE')
                              elif command == 'PRINTLINE':
                                   print(debracket(self.calculator.calculate(value1)),end='\n')
                                   self.trace_stack.add(str(line_counter)+' PRINTLINE ')
                              elif command == 'PRINT':
                                   print(debracket(self.calculator.calculate(value1)),end='')
                                   self.trace_stack.add(str(line_counter)+' PRINT ')
                              elif command == 'END':
                                   self.trace_stack.add(str(line_counter)+' PROGRAM TERMINATED')
                                   break

                    except:
                         self.trace_stack.add(str(line_counter)+' LINE EXCEPTION')

          except:
               self.trace_stack.add(str(line_counter)+' PROGRAM EXCEPTION')
               
     def interpret (self,x):



          self.__init__()
          self.load(x)
          self.find_blocks()
          self.run()

          

          
                         
class Logic:

     
     def __init__ (self,oracle=None):
          self.oracle = oracle 


     def contains (self,phrase,chars):

          """Returns TRUE if <phrase> contains ANY one of <chars>"""

          for x in chars:

               if x in phrase:
                    return True
          return False

     def bracketed (self,phrase):

          """Returns TRUE if <phrase> is encompassed by a left bracket and a right bracket
          at the same hierarchical level"""

          level = 0
          left_point = None
          right_point = None
          

          for count,char in enumerate(phrase):

               if char == '(':
                    if level == 0:
                         left_point = count
                    level+=1
               if char == ')':
                    level-=1
                    if level == 0:
                         right_point = count
          if not (left_point is None)  and (not right_point is None) and left_point == 0 and right_point == len(phrase)-1:
               return True
          return False 

        

     def split_into_phrases (self, phrase):
          
          """Inputs a string and returns a list containing elemenets, split according to parsing rules.
          IF the list is of elements to be combined with AND, then no header.
          If the list if of elements to be combined with OR, then '@' at the head of the list.

          """

          if not self.contains(phrase,'()'):

               #For a phrase without parantheses
               

               if '|' in phrase:
                    return ['@']+[x for x in phrase.split('|')]
               elif '&' in phrase:
                    return [x for x in phrase.split('&')]

          #If the phrase contains parantheses.
          
          phrase = list (phrase)
              #convert string into a list of chars
          level = 0
          found = False # if one of the operators is found in the phrase 

          for operator in ['#','>','|','&']:
               level = 0 # reset level
               if not found:
               
               
                    for x,char in enumerate(phrase):
                         if char == '(':
                              level += 1
                         if char == ')':
                              level -=1
                              # level indicates level within hierarchy established by parantheses

                         if level == 0 and x+1 < len(phrase) and phrase[x+1] == operator:
                              phrase[x+1] = '<<'+operator+'>>'
                              found = True
                              break
                         
                    

          if '<<&>>' in phrase:
               # For AND
               phrases = ''.join(phrase).split('<<&>>')
          elif '<<|>>' in phrase:
               # For OR 
               phrases = ['@']+''.join(phrase).split('<<|>>')
          elif '<<>>>' in phrase:
               # For INFERENCE 
               premise = ''.join(phrase).split('<<>>>')[0]
               conclusion = ''.join(phrase).split('<<>>>')[1]
               phrases = ['@','~'+premise,conclusion]
               #  A => B  translated as ~A OR B
          elif '<<#>>' in phrase:
               # FOR EQUIVALENCY 
               premise = ''.join(phrase).split('<<#>>')[0]
               conclusion = ''.join(phrase).split('<<#>>')[1]
          
               phrase1 = '~'+'('+premise+'&'+'~'+conclusion+')'
               phrase2 = '~'+'('+conclusion+'&'+'~'+premise+')'
               phrases = [phrase1,phrase2]
               # A<>B translated as (~A or B) & (~B or A) 
               
          return [x for x in phrases]

     def all_is_P (self,phrase,predicate_function=None):

          """Returns TRUE if <predicate_function> is TRUE of
          every element in <phrase>"""

          returnvalue = True
          for x in phrase:
               if not predicate_function(x):
                    returnvalue = False
          return returnvalue


     def is_simple (self, phrase):

          """Returns TRUE if <phrase> is a simple name, i.e. a variable"""

          return not self.contains(phrase,'()&|>#')
          
     def is_bool (self, phrase):
          """Returns TRUE if <phrase> is boolean."""
          
          return isinstance(phrase,bool)

     def and_sum (self, phrase):

          """Returns TRUE iff every element in <phrase> is TRUE"""
          for x in phrase:
               if not x:
                    return False
          return True

     def or_sum (self, phrase):

          """Returns TRUE iff one element in <phrase> is TRUE"""
          for x in phrase:
               if x:
                    return True
          return False

     def heading_count(self, phrase,char='~'):

          """Returns the number of negating prefixes in <phrase> and the <phrase> shorn of prefixes."""
          count = 0
          for x in phrase:
               if x  != char:
                    break
               count+=1
          return count,phrase[count:]




     def parse (self, phrase):

          """The primary recursive parsing function"""

          if isinstance(phrase,str):
               #If the phrase is a string
               if self.is_simple(phrase):
                    #EXITS the recursion
                    if phrase[0:2] == '~~':
                         return phrase[2:]
                         #Eliminates negations that cancel each other
                    return phrase
               elif self.bracketed(phrase):
                    #Eliminate top-level parantheses
                    return self.parse(phrase[1:-1])
               elif phrase[0] == '~':
                    #If the phrase begins with a negating prefix...
                    negations,phrase = self.heading_count(phrase)
                    
                    if self.bracketed(phrase):
                         #If the negated phrase is bracketed
                         if negations % 2 == 1:
                              subphrase = self.split_into_phrases(phrase[1:-1])
                              if subphrase[0] != '@':                                     
                                   #De Morgan's Law 
                                   return self.parse(['@']+['~'+x for x in subphrase])
                              else:
                                   #De Morgan's Law
                                   return self.parse(['~'+x for x in subphrase[1:]])
                         else:
                              return self.parse(phrase[1:-1])
                    return self.parse(self.split_into_phrases((negations%2)*'~'+phrase))
                    
               else:
                    return self.parse(self.split_into_phrases(phrase))
          # IF the phrase is a list
          if self.all_is_P(phrase,predicate_function=self.is_simple):
               #If every terms of the phrase list is simple...
               #This prepares for EXIT from recursion
               return [self.parse(x) for x in phrase]
          return self.parse([self.parse(x) for x in phrase])


                    

     def no_or_clauses (self,phrase):
          """ Returns TRUE if <phrase> contains no OR lists."""
          
          for x in phrase:
               if isinstance(x,list) and x[0] == '@':
                    return False
          return True 



     def multiply (self,phrase):

          """Recursive function to combine AND or OR lists.
          The PRODUCT of OR lists is used to generate the TRUTH TABLE.
          """

          if not isinstance(phrase,list):
               return phrase
          
          if self.no_or_clauses(phrase):
               # IF there are only AND lists at the top level


               return [self.multiply(x) for x in phrase]

          else:
               # For a combination of AND and OR lists
               and_clauses = []
               or_clauses = []
               
               for x in phrase:
                    # DIVIDES into AND and OR lists 
                    if isinstance(x,list) and x[0]=='@':
                         or_clauses.append(x)
                    else:
                         and_clauses.append(x)
               multiplied_phrases = [and_clauses]


               for x in or_clauses:
                    # Produces the product of two OR lists.
                    # [A,B][C,D] = [[A,C],[A,D],[B,C],[B,D]]

                    new_phrases = []
                    for y in x[1:]:


                         for z in list(multiplied_phrases):
                              if not isinstance(z,list):
                                   
                                   new_phrases.append([z,y])
                              else:
                                   new_phrases.append(z+[y])
                    multiplied_phrases =  [self.multiply(x) for x in new_phrases]
                    
          return extract_lists(multiplied_phrases)
                         


     def interpret (self,phrase):

          """Recursive function interpreting LIST of AND and OR lists containing BOOLEAN values to
          yield a BOOLEAN value.
          <universe> is the dictionary representing the true facts with reference to which the
          value of <phrase> will be calculated."""


          if phrase is None:
               return phrase

          if isinstance(phrase,str):
               
               if phrase=='@':
                    return '@'
               negations,phrase = self.heading_count(phrase)
               if not self.oracle.contains(phrase):
                    # IF the truth value of phrase not defined in universe.
                    return None
                    
               if negations % 2 == 0:
                    if self.oracle.contains(phrase):
                         # If no negative prefix, return value of phrase in universe.
                         
                         return self.oracle.get(phrase)
               else:
                    if self.oracle.contains(phrase):
                         # If negative prefix...
                              
                         return not self.oracle.get(phrase)
                    
          
          if isinstance(phrase,bool):
               
               return phrase
          elif self.all_is_P(phrase,predicate_function=self.is_bool) or (phrase[0]=='@' and all_is_P(phrase[1:],predicate_function=self.is_bool)):
                    # If an AND or OR LIST, return TRUE or FALSE for the list.
                    if phrase[0]=='@':
                         return self.or_sum(phrase[1:])
                    else:
                         return self.and_sum(phrase)
          phrase = [x for x in phrase if not (x is None)]
               #Eliminate null elements.
          if not phrase:
               return None 
          return self.interpret([self.interpret(x,oracle=oracle) for x in phrase])
               #Recursively calls function.



               
          


          

     

     


class Calculator:

     def __init__(self,register = None):

          def debracket (x):
               if x[0]+x[-1] in ['""',"''"]:
                    return x[1:-1]

          def gcd (x,y):

               return math.gcd(int(x),int(y))

          def flinput (x):
               return float(input(debracket(x)))
          def sinput (x):
               return '"'+str(input(debracket(x)))+'"'
          


          self.operations = ['+','-','*','/','^','%']
              # basic operators in order of evaluation
          # functions imported from math
          self.functions = {'fact':(math.factorial,1,1),
                       'abs':(math.fabs,1,1),
                       'floor':(math.floor,1,1),
                       'fmod':(math.floor,2,2),
                       'frexp':(math.frexp,1,1),
                       'gcd':(gcd,2,2),
                       'remainder':(math.remainder,2,2),
                       'trunc':(math.trunc,1,1),
                       'exp':(math.exp,1,1),
                       'expm1':(math.expm1,1,1),
                       'logn':(math.log,1,1),
                       'logx':(math.log,2,2),
                       'log1p':(math.log1p,1,1),
                       'log2':(math.log2,1,1),
                       'log10':(math.log10,1,1),
                       'pow':(math.pow,2,2),
                       'sum':(math.fsum,1,10000),
                       'acos':(math.acos,1,1),
                       'asin':(math.asin,1,1),
                       'atan':(math.atan,1,1),
                       'atan2':(math.atan2,2,2),
                       'cos':(math.cos,1,1),
                       'hypot':(math.hypot,2,10000),
                       'sin':(math.sin,1,1),
                       'tan':(math.tan,1,1),
                       'degrees':(math.degrees,1,1),
                       'radians':(math.radians,1,1),
                       'acosh':(math.acosh,1,1),
                       'asinh':(math.asinh,1,1),
                       'atanh':(math.atanh,1,1),
                       'cosh':(math.cosh,1,1),
                       'sinh':(math.sinh,1,1),
                       'tanh':(math.tanh,1,1),
                       'erf':(math.erf,1,1),
                       'erfc':(math.erfc,1,1),
                       'gamma':(math.gamma,1,1),
                       'lgamma':(math.lgamma,1,1),
                       'neg':(lambda x:-x,1,1),
                       'inputstring':(sinput,1,1),
                       'inputfloat':(flinput,1,1)}
          if register is None:
               self.current_register = Register()
          else:
               self.current_register = register
               # Initiate register for variables

          self.SCRIPT ="""           SLOTHcalc
                              PROGRAMMABLE CALCULATOR 

               Slow
               Ludic
               Obscolete
               Technology
               Has its place


                                  by
                          Anthony Curtis Adler

         OPERATORS = +,/,-,*,%(mod),^(power), ()
         RELATIONS == != <= >= < >
         FUNCTIONS abs,floor,fmod,frexp,gcd,remainder,
         trunc,exp,expml,logn,logx,log1p,log2,log10,
         power,sum,acos,asin,atan,atan2,cos,hypot,
         sin,tan,degrees,radians,acost,asinh,atanh,cosh,
         sing,tanh,erf,erfc,gamma,lgamma,neg

         CONSTANTS pi, e, tau, inf, nan

         NEWCALC:name  TO OPEN UP A NEW CALCULATOR
         NEWPROGRAM:name TO WRITE A NEW PROGRAM

         IN THE CALCULATOR MODE:

              Any alphanumeric phrase can serve as a variable.
              To return an entry from the log, type @line@.

              ALL to show the log
              
        IN THE PROGRAMMABLE MODE:

        SLOTH is basically a very basic basic.
        COMMANDS INCLUDE:
               PRINT expression
               PRINTLINE expression
               GOTO line#                  
               WHILE conditionalexpression 
               ENDWHILE
               IFSKIP conditionalexpression /If TRUE, then skip the next line
               END
               IS                           /ALTERNATIVE FORM
                                            /OF VARIABLE ASSIGNMENT
                                            /YOU can also use '='
        SPECIAL FUNCTIONS
               inputfloat('PROMPT')
               inputstring('PROMPT')
        INTERPRETER OPERATION
               line numbers can be entered explicitly or implicity
               RUN to run a program for the first time.
               RERUN to run again without reinterpreting
               CLEAR to clear program
               ALL to show program
               CALC:name to return to calc mode
               TRACE to show the trace stack
               DELETE to delete a line

         EXAMPLES

         1) HELLO WORLD
            10 PRINT 'HELLO WORLD'

         2) CALCULATE FIBONACCI NUMBERS

          10 PRINTLINE 'FIBONACCI'
          20 LIMIT = inputfloat('LIMIT?')
          30 OLD=0
          40 NEW=1
          50 COUNTER = 1
          60 WHILE COUNTER<LIMIT
          70 NEWER=OLD+NEW
          80 OLD=NEW
          90 NEW=NEWER
          100 COUNTER=COUNTER+1
          110 PRINT 'VALUE='
          120 PRINTLINE NEW
          130 ENDWHILE
          140 PRINTLINE 'LIMIT'
          150 PRINT LIMIT

 MIT License


Copyright (c) 2020 Anthony Curtis Adler



Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:


The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.


THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
         
"""
          


     def calculate (self,phrase):

          """Core routine for parsing and evaluating phrase"""


          def bracketed (phrase,bracketing='()'):

               """Returns TRUE if <phrase> is encompassed by a left bracket and a right bracket
               at the same hierarchical level"""

               level = 0
               left_point = None
               right_point = None
               

               for count,char in enumerate(phrase):

                    if char == bracketing[0]:
                         if level == 0:
                              left_point = count
                         level+=1
                    if char == bracketing[1]:
                         level-=1
                         if level == 0:
                              right_point = count
               if not (left_point is None)  and (not right_point is None) and left_point == 0 and right_point == len(phrase)-1:
                    return True
               return False

          def quoted (phrase):

               level = 0
               foundchar = ''
               left_point = None
               right_point = None 
               for count,char in enumerate(phrase):

                    if char in ['"',"'"] and level == 0:
                         foundchar = char
                         left_point = count
                         level += 1
                    elif level == 1 and char == foundchar:
                         right_point = count
                         level += 1
               if not (left_point is None)  and (not right_point is None) and left_point == 0 and right_point == len(phrase)-1:
                    return True
               return False 
                         
                         

          def is_function(phrase):

               """Tests to see if a phrase begins with a predefined function,
               in which case it returns information about the iarity of function"""
               
               
               for x in self.functions.keys():

                    if len(x) < len(phrase) and phrase[0:len(x)] == x:
                         if bracketed(phrase[len(x):]):
                              if self.functions[x][1]-1 <= phrase.count(',') <= self.functions[x][2]-1:
                                   return x, self.functions[x][0], self.functions[x][2], phrase[len(x):]
               else:
                    return False,False,False,False 
          

          def all_simple (phrase):

               """Tests if a phrase is a simple string representing an expression, rather than an operation"""


               for x in phrase:
                    if (x not in self.operations and not (isinstance(x,(int,float,bool)) or (isinstance(x,str) and quoted(x)))) or self.current_register.contains(x):
                         return False
               return True
          
          def parse (phrase):

               """Parses and analzes the phrase"""

               if isinstance(phrase,str):
                    if quoted(phrase):
                         return phrase
                    else:
                         try:
                              return float(phrase)
                         except:
                              pass
                         

                    # If the phrase is a string
                    phrase = phrase.strip()

                    func_name, func, iarity, func_phrase = is_function(phrase)
                         # tests is it is function; otherwise the values are false.
                    
                    

                    if func_name:
                         if iarity == 1:
                              # If the function accepts one value
                              return func(parse(func_phrase))
                         if iarity == 2:
                              # Two values 
                              func_phrase = func_phrase[1:-1]
                              term1,term2 = func_phrase.split(',')[0],func_phrase.split(',')[1]
                              return func(parse(term1),parse(term2))
                         if iarity > 2:
                              # A list of values 
                              func_phrase = func_phrase[1:-1]
                              return func([parse(x) for x in func_phrase.split(',')])
                    elif phrase[0] == '-' and bracketed(phrase[1:]):
                         # Translates negative sign (as opposed to operators) into corresponding function 
                         return -parse(phrase[2:-1])


                    elif bracketed(phrase):
                         # removes top-level bracket
                         phrase = phrase[1:-1]
                         return parse(phrase)
                    elif phrase in self.operations:
                         return phrase
                    elif self.current_register.contains(phrase):
                         # for variables and constants
                         return self.current_register.get(phrase)
                    elif phrase and phrase[0]=='@' and phrase[-1]=='@':
                         # to retrieve values from the log 
                         index = int(parse(phrase[1:-1]))
                         if 0<= index <= len(self.lines):
                              return self.lines[index][0]
                    else:
                                        
                         phrase = list(phrase)
                           #phrase is converted to a list to allowing indexical assignments
                         operation_sequence = []
                         level = 0
                         inquotes = False
                         quote_form = ''
                         for counter, x in enumerate(phrase):

                              # Search for operators that are not enclosed in parantheses

                              if not inquotes and x in ['"',"'"]:
                                   inquotes = True
                                   quote_form = x
                              elif inquotes and x == quote_form:
                                   if counter < len(phrase)-1:
                                        if phrase[counter+1] in ['+']:
                                             phrase[counter+1] = '#+#'

                              if x == '(':
                                   level +=1

                              if x == ')':
                                   level -=1
                              if level == 0:
                                   if counter<len(phrase)-1:
                                        if phrase[counter+1] in self.operations:
                                             # If an operator is found, surround it with pound signs
                                             phrase[counter+1] = '#'+phrase[counter+1]+'#'
                                             if phrase[counter+2] in self.operations:
                                                  phrase[counter+2] = '~'
                                                  # For a minus sign that is not an operator

                                             
                         phrase = ''.join(phrase).replace('~','-').split('#')
                           # Split the phrase into expressions linked by operators 
                         newphrase = []
                         for x in phrase:
                              # a clumsy way to distinction between numerical values, and string operators
                              try:
                                   newphrase.append(float(x))
                              except:
                                   newphrase.append(x)
                         phrase = newphrase

                         return parse(phrase)
                         
                    

               if isinstance(phrase,list):
                    # If the phrase has already been parsed into a list 
                    if len(phrase) == 1:
                         return (parse(phrase[0]))
                    if all_simple(phrase):
                         # If every value in the phrase list has been reduced to
                         # a numerical value or an operator
                        

                         for operation in self.operations:

                              #In order to preserve the correct order of operations,
                              #the operations are analyzed in succession

                              while operation in phrase:

                                   #This repeat as long as the operation is in the phrase,
                                   #since with each pass it only "reduced"
                                   #expression/operator/expression triplet
                                   

                                   newlist = [] # For the result of each pass through the list.
                                   lastvalue = None
                                   counter = 0
                                   stop = False
                                   while counter < len(phrase) and not stop:
                                        
                 
                                        if counter < len(phrase)-2:
                                             a = phrase[counter]
                                             op = phrase[counter+1]
                                             b = phrase[counter+2]
                                               #take a triplet of values from the list

                                             if op == operation:
                                                  # if an operator is found, reduced the triplet, and
                                                  # then add the reduced value, together with the rest
                                                  # of the list to the 
                                                  if operation == '*':
                                                       c = a*b
                                                  elif operation == '+':
                                                       if isinstance(a,str) and isinstance(b,str):
                                                            c = a[0:-1]+b[1:]
                                                       else:
                                                            c = a+b
                                                  elif operation == '/':
                                                       c = a/b
                                                  elif operation == '^':
                                                       c = a**b
                                                  elif operation == '%':
                                                       c = a % b
                                                  elif operation == '-':
                                                       c = a - b
                                                  newlist.append(c)
                                                  newlist += phrase[counter+3:] 
                                                  stop = True
                                             else:
                                                  newlist.append(a)
                                        else:
                                             # otherwise, just add the text value to the new list
                                             newlist.append(phrase[counter])
                                        counter +=1 
                                             
                                   
                                   phrase = newlist



                                   
                         
                    else:
                        # if the list is not yet simple, return a new list after parsing each element.
                        phrase = [parse(x) for x in phrase]
                    return parse(phrase)

               if isinstance(phrase,(int,float)):
                    # if a numerical value, stop the recursion
                    return phrase 

          return parse(phrase)


     def show_line (self,counter,x):

          return str(counter)+':'+str(x[1])+(20-len(str(x[1])))*' '+'|'+x[0]
     

     def show_all (self):

          #Shows all the lines in the log

          for counter, x in enumerate(self.lines):
               print(self.show_line(counter,x))
               
     def clear (self):
          self.lines = [('',0)]
          self.counter = 0

     def delete(self,x):

          if '-' not in x:
               x = int(x)
               if 0 <= x < len(self.lines):
                    indexes = [x]
          else:
               x_from, x_to = int(x.split('-')[0]),int(x.split('-')[1])
               if 0 <= x_from < x_to <= len(self.lines):
                    indexes = range(x_from,x_to+1)
          if indexes:
               for ind in indexes:

                    print('DELETED/',self.show_line(ind,self.lines[ind]))
                    self.lines[ind] = None
          self.lines = [x for x in self.lines if x]

     def new_calc(self,x):
          self.scriptname = x
          if x not in self.scripts:
               self.scripts[x] = (0,[('',0)])
          self.counter = self.scripts[x][0]
          self.lines = self.scripts[x][1]
          self.show_counter = 0
          self.programming = False

     def new_program(self,x):
          self.scriptname = x
          if x not in self.scripts:
               self.scripts[x] = (0,[('',0)])
          self.counter = self.scripts[x][0]
          self.lines = self.scripts[x][1]
          self.show_counter = 0
          self.programming = True 
          self.entered_lines = {int(x.split(']')) for x in self.lines if x[0].split('[')[0].isnumeric()}
class Programmable(Calculator):

     

         
     def console (self):

          # The console operating the calculator 

          self.commands = {'ALL':self.show_all,
                           'CLEAR':self.clear}
          self.one_commands = {'DELETE':self.delete,
                               'NEWCALC':self.new_calc,
                               'NEWPROGRAM':self.new_program}
          self.programming = False
          

          
          self.show_counter = 0
          self.scripts = {}
          self.script = ''
          self.scripts['main'] = (0,[('',0)])
          self.scriptname = 'main'
          self.lines = self.scripts[self.scriptname][1]
          self.counter = self.scripts[self.scriptname][0]
          print(self.SCRIPT)
          self.entered_lines = set()
          while True:

               

               
               
               if self.programming:

                    newnumber = 0

                    def get_line (line_no):

                         for counter, x in enumerate(self.lines):
                              if x[0].split(' ')[0].isnumeric() and int(x[0].split(' ')[0]) == line_no:
                                   return counter
                         return self.counter
                    
                    query = input(self.scriptname+'[')


                    if query.strip() == 'RUN':
                         self.computer = Program()
                         script = '\n'.join(x[0] for x in self.lines)
                         
                         self.computer.interpret(script)
                         print()
                                             
                    elif query.strip() == 'RERUN':
                         if self.computer:
                              self.computer.run()
                         print()
                    elif query.strip() == 'ALL':
                         self.script =  '\n'.join(x[0] for x in self.lines)
                         print(self.script)
                         print()
                    elif (':' in query.strip()
                          and query.strip().split(':')[0]=='DELETE'):
                         if int(query.strip().split(':')[1]) in self.entered_lines:
                              if query.strip().split(':')[1].isnumeric():
                                   to_delete = get_line (int(query.strip().split(':')[1]))

                                   self.lines.pop(to_delete)
                                   self.entered_lines.remove(int(query.strip().split(':')[1]))
                              
                    elif query.strip() == 'TRACE':
                         print('\n'.join(self.computer.trace_stack.stack))
                    elif query.strip() == 'CLEAR':
                         self.lines = [('',0)]
                         self.entered_lines = set()
                         self.counter = 0
                    elif len(query.strip())>3 and query.strip()[0:5]  == 'CALC':
                         if ':' in query.strip():
                              self.new_calc(query.strip().split(':')[1])
                         else:
                              self.new_calc('main')

                    else:
                    
                         

                         
                         if query and not query.split(' ')[0].isnumeric() and query[0] != '@':
                              if self.entered_lines:
                                   newnumber= int(max(self.entered_lines)/10)*10+10
                              else:
                                   newnumber = 10
                              query=str(newnumber)+' '+query
              
                         
                         if  ' ' in query and query.split(' ')[0].isnumeric():
                              command_line,command = int(query.split(' ')[0]),' '.join(query.split(' ')[1:])
                              print(command_line,'/',command)
                              if command_line in self.entered_lines:

                                   self.counter = get_line (command_line)
                                   self.lines[self.counter] = (query,0)
                              elif self.entered_lines and command_line < min(self.entered_lines):
                                   self.lines = [(query,0)]+self.lines 
                              elif self.entered_lines and command_line < max(self.entered_lines):
                                   less_than = sorted([x for x in self.entered_lines if x<command_line])
                                   if less_than:
                                        left_bound= len(less_than)
                                   self.lines = self.lines[0:left_bound+1] + [(query,0)] + self.lines[left_bound+1:]
                                        
                                        
                                   
                              else:
                                   self.entered_lines.add(command_line)
                                   self.counter += 1
                                   self.lines.append((query,0))
                                   
                                   
                              print(str(self.counter)+'|'+' '+query)

                         elif query and query[0]=='@':
                              query=query[1:]
                              try:
                                   print(self.calculate(query))
                              except:
                                   print('INVALID INPUT')
                         if newnumber:
                              self.entered_lines.add(newnumber)

                                   
                      
                              
                         
                    
               
               else:
                    query = input(self.scriptname+'@')
                    
                    if '---' in query:
                         query = query.replace('---','-')
                              #eliminate redundant minus signs

                    if query in self.commands:
                         self.commands[query]()
                              #for system commands
                    elif query.split(':')[0] in self.one_commands:
                         if ':' in query:
                              self.one_commands[query.split(':')[0]](query.split(':')[1])
                    elif query == 'QUIT':
                              #to quit
                         break
                    elif query[0:5]=='GOTO:':
                         line = int(query.split(':')[1])
                         if 0 <= line <len(self.lines):
                              self.counter = line
                         else:
                              print('INVALID INPUT')
                    
                    else:

                         
                         if query:
                              self.counter +=1 
                              if query[0] in self.operations:
                                   query = str(self.lines[self.counter-1][1])+query
                                      # if no initial value, perform operation on previous value


                              if '=' in query:
                                      # To define a variable (=subject)
                                   subject, predicate = query.split('=')
                                   subject = subject.strip()
                              else:
                                      # If not variable = subject 
                                   predicate = query
                                   subject = ''
                              try:
                                   value = self.calculate(predicate)
                              except:
                                   value = 'ERROR'
                              if subject:
                                     # if a variable has been given, define its value 
                                   if not isinstance(value,str):
                                        # to make sure that an ERROR message is not recorded as a value 
                                        self.current_register.set(subject,value)
                              else:
                                    # If the counter is not yet at the end of the log 
                                   if self.counter < len(self.lines):
                                        self.lines[self.counter] = (query,value)
                                   else:
                                        # Otherwise just append query and result-value to log 
                                        self.lines.append((query,value))
                              print(' '+subject+' '*(24-len(subject))+'|',predicate,'=',value)
                         else:
                              if self.show_counter < len(self.lines)-1:
                                   self.show_counter+=1
                              print (self.self.show_counter,':',
                                     str(self.lines[self.show_counter][1])
                                     +(20-len(str(self.lines[self.show_counter][1])))*' ',
                                     '|',self.lines[self.show_counter][0])
                              if self.show_counter == len(self.lines)-1:
                                   self.show_counter = 0
                         if self.counter > len(self.lines)-1:
                              self.counter = len(self.lines)-1
                              
                              

                    




if __name__ == '__main__':

     calc = Programmable(register=Register())
     calc.console()

                      
                    
