import sax


def directional_coupler(coupling=0.5):
    kappa = coupling**0.5
    tau = (1 - coupling) ** 0.5
    sdict = sax.reciprocal(
        {
            ("port0", "port1"): tau,
            ("port0", "port2"): 1j * kappa,
            ("port1", "port3"): 1j * kappa,
            ("port2", "port3"): tau,
        }
    )
    return sdict
