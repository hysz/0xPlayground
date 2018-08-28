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

# Returns True iff there exists a `leftMaker` that could be returned by `Exchange.fillOrder`,
# given `rightMaker`, `rightTaker`, and `leftTaker
def isValidFillResult_Right(c):
  for i in range(1, c.rightTaker + 1):
    if math.floor((c.rightMaker / c.rightTaker) * i) == c.leftTaker:
      return True
  return False

def notValidFillResult_Right(c):
  return not(isValidFillResult_Right(c))

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
    notValidFillResult_Right
  ])
test5()