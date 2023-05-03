
def generate_amoritization_schedule(interest: float, term: int, principal: float):
    '''
    Generates the principal and interest portion payments for the lifetime of a loan

    Parameters
    ----------
    interest : float
        The interest rate of the loan expressed as percentage. A 3.5% APR would be input as 3.5
    term : int
        The number of months of the loan. A 3 year mortgage would be input as 120.
    principal : float
        The original amount borrowed. $30,000 loan would be input as 30000

    Returns
    -------
    list
        A list of tuples that represent the payment portions for a given month of a repayment schedule (principal, interest)
    '''
    result = []
    remaining_principal = principal
    total_monthly_payment = _calculate_total_monthly_payment(interest, term, principal)
    
    while remaining_principal > 0:
        principle_portion = _calculate_principle_payment(total_monthly_payment, remaining_principal, interest)
        interest_portion = total_monthly_payment - principle_portion
        remaining_principal -= principle_portion
        result.append((round(principle_portion, 2), round(interest_portion, 2)))
    
    return result

def _calculate_principle_payment(total_monthly_payment:float, outstanding_balance: float, interest: float):
    '''
    Calculates the principal portion of a given monthly loan payment

    Parameters
    ----------
    total_monthly_payment : float
        The total amount owed on a loan on any given month.
    outstanding_balance : float
        The total remaining principal on the loan
    interest : float
        The interest rate of the loan expressed as percentage. A 3.5% APR would be input as 3.5

    Returns
    -------
    float
        The principal portion of the total monthly payment
    '''

    monthly_interest = (interest / 100) / 12
    result = total_monthly_payment - (outstanding_balance * monthly_interest)
    return result



def _calculate_total_monthly_payment(interest: float, term: int, principal: float):
    '''
    Calculates the total monthly payment for a loan assuming monthly payments

    Parameters
    ----------
    interest : float
        The interest rate of the loan expressed as percentage. A 3.5% APR would be input as 3.5
    term : int
        The number of months of the loan. A 3 year mortgage would be input as 120.
    principal : float
        The original amount borrowed. $30,000 loan would be input as 30000

    Returns
    -------
    float
        The total monthly payment that would need to be made throughout the life of the loan
    '''

    monthly_interest = (interest / 100) / 12
    numerator = monthly_interest * pow((1 + monthly_interest), term)
    denominator = (pow((1 + monthly_interest), term)) - 1
    result = principal * (numerator / denominator)
    return result