import sys
import math

def isRoundingErrorFloor(numerator, denominator, target):
  #print(remainder)
  if target == 0 or numerator == 0:
    return False
    #print "remainder = (%d * %d) MOD %d" % (target, numerator, denominator)
  remainder = (target * numerator) % denominator

  isError = (1000 * remainder) >= (numerator * target)
  #print(errPercentageTimes1000000)
  return isError

def isRoundingErrorCeil(numerator, denominator, target):
  #print(remainder)
  if target == 0 or numerator == 0:
    return False
    #print "remainder = (%d * %d) MOD %d" % (target, numerator, denominator)
  remainder = (target * numerator) % denominator
  remainder = (denominator - remainder) % denominator

  isError = (1000 * remainder) >= (numerator * target)
  #print(errPercentageTimes1000000)
  return isError

def needsRounding(numerator, denominator, target):
  return (numerator * target) % denominator != 0

def getPartialAmountFloor(numerator, denominator, target):
  return math.floor((numerator * target) / denominator)

def getPartialAmountCeil(numerator, denominator, target):
  return math.ceil((numerator * target) / denominator)

class Candidate:
  def __init__(self):
    self.leftMaker = 0
    self.leftTaker = 0
    self.rightMaker = 0
    self.rightTaker = 0

  def output(self):
    print "[%d, %d], [%d, %d]"%(self.leftMaker, self.leftTaker, self.rightMaker, self.rightTaker)

def hasNegativeSpread(c):
  return c.leftMaker * c.rightMaker > c.leftTaker * c.rightTaker

def bothOrdersFullyFilled(c):
    return s.leftTaker == s.rightMaker

def leftOrderFullyFilled(c):
  return c.leftTaker <= c.rightMaker

def rightOrderFullyFilled(c):
  return c.leftTaker >= c.rightMaker

# In the matching algorithm, does this candidate fall under "Case 1:Left Fills Right"?
def isLeftFillsRight(c):
  return c.leftTaker >= c.rightMaker

def leftSellParameters_LeftFillsRight(c):
  return (c.leftMaker, c.leftTaker, c.rightMaker)

def needsRounding_LeftFillsRight(c):
  return needsRounding(*leftSellParameters_LeftFillsRight(c))

def hasRoundingErrorCeil_LeftFillsRight(c):
  return isRoundingErrorCeil(*leftSellParameters_LeftFillsRight(c))

def hasRoundingErrorFloor_LeftFillsRight(c):
  return isRoundingErrorFloor(*leftSellParameters_LeftFillsRight(c)) 

def noRoundingErrorFloor_LeftFillsRight(c):
  return isRoundingErrorFloor(*leftSellParameters_LeftFillsRight(c)) == False

# In the matching algorithm, does this candidate fall under "Case 1:Right Fills Left"?
def isRightFillsLeft(c):
  return c.leftTaker < c.rightMaker

def rightBuyParameters_RightFillsLeft(c):
  return (c.rightTaker, c.rightMaker, c.leftTaker)

def needsRounding_RightFillsLeft(c):
  return needsRounding(*rightBuyParameters_RightFillsLeft(c))

def hasRoundingErrorCeil_RightFillsLeft(c):
  return isRoundingErrorCeil(*rightBuyParameters_RightFillsLeft(c))

def noRoundingErrorCeil_RightFillsLeft(c):
  return isRoundingErrorCeil(*rightBuyParameters_RightFillsLeft(c)) == False

def hasRoundingErrorFloor_RightFillsLeft(c):
  return isRoundingErrorFloor(*rightBuyParameters_RightFillsLeft(c)) 

def noRoundingErrorFloor_RightFillsLeft(c):
  return isRoundingErrorFloor(*rightBuyParameters_RightFillsLeft(c)) == False


# There are cases where order matching creates fill amounts [amountToSell, amountToBuy]
# that are unattainable from Exchange.fillOrder.
# This function returns true iff matching the orders in `c` would yield fill amounts for the right order 
# that are unattainable by Exchange.fillOrder.
def matchingResultIsAttainableByFillOrder_RightFillsLeft(c):
  # The left order is fully filled by the right order,
  # so the right maker must sell c.leftTaker units of their asset.
  #
  # In return the right maker receives math.ceil((c.rightTaker/c.rightMaker) * c.leftTaker) units
  # of the left maker's asset.
  #
  # The question: is it possible for these fill amounts to be obtained by calling Exchange.fillOrder?
  # 
  # Valid fill results produced by fillOrder follow a stepwise function:
  #  y = math.floor(mx); where m is order.makerAmount/order.takerAmount
  # 
  # Because x is a natural number, the increments on the y-axis follow a peacewise function, where:
  # yDelta = {
  #            math.floor(order.makerAmount/order.takerAmount)  ; when (mx)%y != 0
  #            math.ceil(order.makerAmount/order.takerAmount)   ; when mx%y == 0
  #          } the y-values increment units at a time 
  # 
  # In the case of order matching where the left order is fully filled, we instead have:
  #  y = math.ceil(mx)
  #  yDelta = math.ceil(order.makerAmount/order.takerAmount)
  # 
  # It follows that yDelta differs between order matching and exchange.fillOrder
  # iff (mx)%y != 0
  # And,
  # If yDelta differs for a given x, then so does y.
  #
  # This function seeks to find a value y that exists in oredr matching that 
  # cannot exist in exchange.fillOrder. 
  # That is:
  #   There exists x_1 such that y_1 = matc.ceil(mx_1), and 
  #   there exists no x_2 such that y_1 = math.floor(mx_2)
  # 
  # The input `c` to this function has a fixed x_1 and y_1.
  # We return True iff no such x_2 exists.
  #
  
  # Search for such an x_2 starting at x_1
  x_1 = math.ceil((c.rightTaker * c.leftTaker) /c.rightMaker)
  y_1 = c.leftTaker
  x_2 = x_1
  y = math.floor((c.rightMaker * x_2) / c.rightTaker)
  if y == y_1:
    return True
  elif y < y_1:
    while y < y_1:
      x_2 += 1
      y = math.floor((c.rightMaker * x_2) / c.rightTaker)
    if y == y_1:
      return True
    return False
  else: # y > y_1
    while y > y_1:
      x_2 -= 1
      y = math.floor((c.rightMaker * x_2) / c.rightTaker)
    if y == y_1:
      return True
    return False

  raise Exception('Search failed. Should not hit this point')
  
def matchingResultNotAttainableByFillOrder_RightFillsLeft(c):
  return not(matchingResultIsAttainableByFillOrder_RightFillsLeft(c))

# Returns True iff there exists a `rightTaker` that could be returned by `Exchange.fillOrder`,
# given `leftMaker`, `leftTaker`, and `rightMaker`
def isValidFillResult_Left(c):
  for i in range(1, c.leftMaker + 1):
    if math.floor((c.leftTaker / c.leftMaker) * i) == c.rightTaker:
      return True
  return False

def notValidFillResult_Left(c):
  return not(isValidFillResult_Left(c))

def search(
  filters,
  maxResults = 1,
  minLeftMaker = 1,
  maxLeftMaker = 100,
  minLeftTaker = 1,
  maxLeftTaker = 100,
  minRightMaker = 1,
  maxRightMaker = 100,
  minRightTaker = 1,
  maxRightTaker = 100
):
  candidate = Candidate()
  results = 0
  for candidate.leftMaker in range(minLeftMaker, maxLeftMaker + 1):
    for candidate.leftTaker in range(minLeftTaker, maxLeftTaker + 1):
      for candidate.rightMaker in range(minRightMaker, maxRightMaker + 1):
        for candidate.rightTaker in range(minRightTaker, maxRightTaker + 1):
          # Iterate filters
          passedFilters = True
          for filter in filters:
            if filter(candidate) == False:
              passedFilters = False
              break
          
          if not(passedFilters):
            continue
          
          # Candidate passed all filters!
          candidate.output()
          results += 1
          if results == maxResults:
            return
  
def test1():
  print("Should transfer correct amounts when right order is fully filled and values pass isRoundingErrorFloor but fail isRoundingErrorCeil")
  search([
    hasNegativeSpread,
    isLeftFillsRight,
    needsRounding_LeftFillsRight,
    noRoundingErrorFloor_LeftFillsRight,
    hasRoundingErrorCeil_LeftFillsRight
  ])
# test1()

def test2():
  print("Should transfer correct amounts when left order is fully filled and values pass isRoundingErrorCeil but fail isRoundingErrorFloor")
  search([
    hasNegativeSpread,
    isRightFillsLeft,
    needsRounding_RightFillsLeft,
    noRoundingErrorCeil_RightFillsLeft,
    hasRoundingErrorFloor_RightFillsLeft
  ])
# test2()

def test3():
  print("Should give right maker a better buy price when rounding")
  search([
    hasNegativeSpread,
    isRightFillsLeft,
    needsRounding_RightFillsLeft,
    noRoundingErrorCeil_RightFillsLeft
  ])
# test3()

def test4():
  print("Should give left maker a better sell price when rounding")
  search([
    hasNegativeSpread,
    isLeftFillsRight,
    needsRounding_LeftFillsRight,
    noRoundingErrorFloor_LeftFillsRight
  ])
# test4()

def test5():
  print("Should transfer correct amounts when right order fill amount deviates from amount derived by `Exchange.fillOrder`'")
  search([
    hasNegativeSpread,
    isRightFillsLeft,
    noRoundingErrorCeil_RightFillsLeft,
    matchingResultNotAttainableByFillOrder_RightFillsLeft
  ])
test5()

'''
def test6():
  print("Should transfer correct amounts when left order fill amount deviates from amount derived by `Exchange.fillOrder`'")
  search([
    hasNegativeSpread,
    isLeftFillsRight,
    noRoundingErrorFloor_LeftFillsRight,
    notValidFillResult_Left
  ])
test6()
'''

'''
for x in range(100000, 100100):
  for y in range(x+1, 100100):
    foundA = False
    for a in range(2, x):
      if (y * a) % x == 0 and (y % x != 0):
        foundA = True
        break
    if not foundA:
      print "(x=%d, y=%d, a=%d)"%(x, y, 1)
        '''