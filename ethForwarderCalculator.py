import math

class Order(object):
    makerAssetAmount = 0.
    takerAssetAmount = 0.
    makerFeeAmount = 0.
    takerFeeAmount = 0.

    def __init__(self, makerAssetAmount, takerAssetAmount, makerFeeAmount, takerFeeAmount):
        self.makerAssetAmount = makerAssetAmount
        self.takerAssetAmount = takerAssetAmount
        self.makerFeeAmount = makerFeeAmount
        self.takerFeeAmount = takerFeeAmount

    def getTakerFillAmount(self, makerFillAmount):
        # Round up because exchange rate favors Maker
        return math.ceil((makerFillAmount * self.takerAssetAmount) / self.makerAssetAmount)

    def getTakerFeeAmount(self, takerFillAmount):
        # Round down because Taker fee rate favors Taker
        return math.floor((takerFillAmount * self.takerFeeAmount) / self.takerAssetAmount)

    def getMakerFillAmount(self, takerFillAmount):
        # Round down because exchange rate favors Maker
        return math.floor((takerFillAmount * self.makerAssetAmount) / self.takerAssetAmount)

    def getMakerFeeAmount(self, makerFillAmount):
        # Round down because Maker fee rate favors Maker
        return math.floor((makerFillAmount * self.makerFeeAmount) / self.makerAssetAmount)
    
    def getTakerFillAmountWithFee(self, makerFillAmount):
        takerFillAmount = self.getTakerFillAmount(makerFillAmount)
        makerFillAmountRemaining = takerFeePaid = self.getTakerFeeAmount(takerFillAmount)
        makerAmountFilled = makerFillAmount - makerFillAmountRemaining
        return (takerFillAmount, makerAmountFilled, makerFillAmountRemaining)

    def getTakerFillAmountWithFeeRecursive(self, makerFillAmount):
        # NOTE - *Not* current implementation of Forwarding Contract.
        #        Using this design we recursively fill the same order until we have enough ZRX.
        #        This function provides an upperbound on ETH required using a geometric series of fills.
        # Amount of fee paid by taker per unit of taker asset
        f = float(self.takerFeeAmount) / self.takerAssetAmount

        # Power at which mf^power = 1/m
        # We want the value of power where mf^power < 1/m
        # Power must also be integral because the algorithm increments power by 1 on each iteration.
        # So, round power down to the nearest integer value and then add 1.
        # This will be the first integer value at which mf^power < 1/m
        power = math.floor( math.log(1, f) - math.log(makerFillAmount, f) ) + 1
        
        # Compute the geometric sum for m + mf + mf^2 + ... mf^(power-1)
        fN = math.pow(self.takerFeeAmount, power) / math.pow(self.takerAssetAmount, power)
        adjustedMakerFillAmount = math.floor( makerFillAmount * ( (1 - fN) / (1 - f)) )
        return (self.getTakerFillAmount(adjustedMakerFillAmount), adjustedMakerFillAmount)

class FeePercentage(object):
    numerator = 0.
    denominator = 1.

    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator

def computeForwarderFee(totalTakerFillAmount, feePercentage):
    return math.floor( (totalTakerFillAmount * feePercentage.numerator) / feePercentage.denominator)

def computeTotalTakerAssetAmount(order, feeOrder, makerFillAmount, feePercentage, doRecursive = False):
     # Amount to fill order
    takerFillAmountForOrder = order.getTakerFillAmount(makerFillAmount)
    print "Must spend %.2f ETH on MakerAsset"%takerFillAmountForOrder

    takerFeeAmountForOrder = order.getTakerFeeAmount(takerFillAmountForOrder)
    print "Must pay %.2f ZRX on fees for MakerAsset"%takerFeeAmountForOrder

    takerAssetAmountForFeeOrder = 0
    if takerFeeAmountForOrder > 0 and doRecursive == True:
        # Amount to fill fee order
        takerAssetAmountForFeeOrder, adjustedTakerFeeAmountForOrder = feeOrder.getTakerFillAmountWithFeeRecursive(takerFeeAmountForOrder)
        print "Recursive Strategy: We spend %.2f ETH to buy %.2f ZRX"%(takerAssetAmountForFeeOrder, adjustedTakerFeeAmountForOrder)
    elif takerFeeAmountForOrder > 0:
        takerAssetAmountForFeeOrder, takerFeeAmountForOrderFilled, takerFeeAmountForOrderRemaining = feeOrder.getTakerFillAmountWithFee(takerFeeAmountForOrder)
        print "Spend %.2f ETH to buy %.2f ZRX and will have %.2f ZRX left to buy"%(takerAssetAmountForFeeOrder,takerFeeAmountForOrderFilled,takerFeeAmountForOrderRemaining)
    else:
        # Do nothing
        print "No Fees to buy."
        
    # Compute fee
    totalTakerFillAmount = takerFillAmountForOrder + takerAssetAmountForFeeOrder
    print "Must spend %.2f ETH to fill order + feeOrder"%totalTakerFillAmount
    forwarderFee = computeForwarderFee(totalTakerFillAmount, feePercentage)
    print "Must pay a fee of %.2f ETH to forwarding contract operator"%forwarderFee

    # Compute total amount to send
    totalAmountToSend = totalTakerFillAmount + forwarderFee
    print "Must send %.2f ETH to forwarding contract"%totalAmountToSend


############### TESTS ###############
# NOTE - the makerFee is zeroed in tests bc it's not needed by client.

def simpleTest():
    order = Order(20., 100., 0., 1000.)
    feeOrder = Order(50000., 2000., 0., 190.)
    makerFillAmount = 10.
    feePercentage = FeePercentage(4567, 10000)
    computeTotalTakerAssetAmount(order, feeOrder, makerFillAmount, feePercentage)

simpleTest()
