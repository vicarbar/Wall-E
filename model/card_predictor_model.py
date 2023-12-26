
from scipy.stats import poisson

# Poisson model for the cards predictor
# lambdas = dict with local lambda, visitor lambda and referee lambda
def poisson_model(lambdas):
    num_tarjetas = range(0, 10)
    prob_combinada = (lambdas['lambda_local'] + lambdas['lambda_visitante'] + lambdas['lambda_arbitro']) / 3
    return {"prediccion": prob_combinada, "probabilidades": list(poisson.pmf(num_tarjetas, prob_combinada))}