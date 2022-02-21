
# Main Cluster Experiments

The example towns designed in this section correspond to most of the experiments in our final paper. We divide this into several parts based on the nature of the experiments.

### Base run with default parameters [Fig 8b, Fig 10a in the paper]
The experiment here is executed with the default parameters of the simulator and a sample town that we designed.
* town_0: Normal run with expected parameters, i.e. base run.

### Manipulation of disease properties [Fig 10b, Fig 11a  in the paper]
Here we apply different infectious and immunity rates.

* town_1: Increase infectious Rate {0.55, 0.6}
* town_2: Increase infectious rate {0.5, 0.9}
* town_3: Increase infectious rate {0.8, 0.95}
* town_4: Increase immunity {0.4, 0.6}
* town_5: Increase immunity {0.8, 0.9}
* town_6: Increase infectious rate {0.1, 0.9}
* town_7: Increase immunity {0.5, 0.6}
* town_8: Increase immunity {0.1, 0.2}
* town_9: Increase immunity and infectious {0.4, 0.6}
* town_10: Decrease Immunity {0.02, 0.03}

### Various Quarantine Policies [Fig 13a  in the paper]

* town_11: Quarantine diseased people on day 200.
* town_12: Quarantine diseased people on day 100.
* town_13: Quarantine diseased people on day 40.
* town_14: Quarantine diseased people on day 60.

#### Probabilistic Quarantine [Fig 13b]
* town_15: 50% probabilistic quarantine diseased people on day 60.
* town_16: 50% probabilistic quarantine diseased people on day 100.
* town_17: 20% probabilistic quarantine diseased people on day 60.
* town_18: 20% probabilistic quarantine diseased people on day 100.

#### Initially infecteds [Fig 11b  in the paper]
* town_19: Reduce the number of initially infected people.



#### Quarantine/Unquarantine Sequence [Fig 12b  in the paper]
* town_20: Quarantine and Unquarantine on days 10, 15.
* town_21: Quarantine and Unquarantine on days 15, 20.
* town_22: Quarantine and Unquarantine on days 20, 40.
* town_23: Quarantine and Unquarantine on days 40, 60, 100, 200.
* town_24: Quarantine and Unquarantine on days 100, 200.


### Restrict communities or groups [Fig 14  in the paper]
* town_25: Restrict workers with a ratio of 30% on day 100.
* town_26: Restrict workers with a ratio of 60% on day 100.
* town_27: Restrict workers with a ratio of 90% on day 100.
* town_28: Close medium and large workspaces on day 60.
* town_29: Close gyms, restaurants, and cinemas on day 60.
* town_30: Close public transportation and malls on day 60.


### Quarantine Control Policies [Fig 15  in the paper]
* town_31: Quarantine diseased people for infected/all > 0.2.
* town_32: Quarantine diseased people for infected/all > 0.1.
* town_33: Quarantine/Unquarantine diseased people for 0.15 > infected/all > 0.1.


### More on Disease Properties [Fig 12a  in the paper]

* town_34: Increase the mortality rate.
* town_35: Increase the incubation period by 3.5 days.
* town_36: Decrease the incubation period by 3.5 days.
* town_37: Decrease the disease period by 7 days.
* town_38: Increase the disease period by 7 days.
