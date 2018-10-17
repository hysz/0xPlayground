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
    
    def getTakerFillAmountForFeeOrder(self, makerFillAmount):
        # For each unit of TakerAsset we buy (MakerAsset - TakerFee)
        adjustedTakerFillAmount = math.ceil( (makerFillAmount * self.takerAssetAmount) / (self.makerAssetAmount - self.takerFeeAmount))
        # The amount that we buy will be greater than makerFillAmount, since we buy some amount for fees.
        adjustedMakerFillAmount = self.getMakerFillAmount(adjustedTakerFillAmount)
        return (adjustedTakerFillAmount, adjustedMakerFillAmount)

class FeePercentage(object):
    numerator = 0.
    denominator = 1.

    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator

def computeForwarderFee(totalTakerFillAmount, feePercentage):
    return math.floor( (totalTakerFillAmount * feePercentage.numerator) / feePercentage.denominator)

# Takes 1 regular order (makerAsset != feeAsset) and 1 fee order (makerAsset == feeAsset)
# to show how computation differs between the two.
def computeTotalTakerAssetAmount(order, feeOrder, makerFillAmount, feePercentage):
     # Amount to fill order
    takerFillAmountForOrder = order.getTakerFillAmount(makerFillAmount)
    print "Must spend %.2f ETH on MakerAsset"%takerFillAmountForOrder

    takerFeeAmountForOrder = order.getTakerFeeAmount(takerFillAmountForOrder)
    print "Must pay %.2f ZRX on fees for MakerAsset"%takerFeeAmountForOrder

    takerAssetAmountForFeeOrder = 0
    if takerFeeAmountForOrder > 0:
        adjustedTakerFillAmount, adjustedMakerFillAmount = feeOrder.getTakerFillAmountForFeeOrder(takerFeeAmountForOrder)
        print "Spend %.2f ETH to buy %.2f ZRX"%(adjustedTakerFillAmount,adjustedMakerFillAmount)
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