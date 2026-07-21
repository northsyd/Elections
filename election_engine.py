import csv
import json
from collections import Counter, defaultdict


# ==========================
# LOAD DATA
# ==========================


def load_candidates():

    candidates = defaultdict(dict)

    with open("data/candidates.csv") as file:

        reader = csv.DictReader(file)

        for row in reader:

            candidates[row["role"]][row["candidate"]] = {
                "colour": row["colour"]
            }

    return candidates





def load_ballots():

    ballots = defaultdict(list)

    with open("data/current_election.csv") as file:

        reader = csv.DictReader(file)

        for row in reader:

            preferences = []

            for key,value in row.items():

                if key.startswith("pref") and value:

                    preferences.append(value)


            ballots[row["role"]].append(
                preferences
            )


    return ballots





def load_previous():

    previous = defaultdict(dict)

    with open("data/previous_election.csv") as file:

        reader = csv.DictReader(file)

        for row in reader:

            previous[row["role"]][row["candidate"]] = float(
                row["first_preference_percent"]
            )


    return previous





# ==========================
# PREFERENTIAL COUNTING
# ==========================


def count_election(ballots):

    candidates=[]

    for ballot in ballots:

        for candidate in ballot:

            if candidate not in candidates:

                candidates.append(candidate)



    active=candidates.copy()

    rounds=[]

    flows=[]



    while True:

        counts=Counter()



        for ballot in ballots:

            for preference in ballot:

                if preference in active:

                    counts[preference]+=1

                    break



        rounds.append(dict(counts))


        total=sum(counts.values())



        for candidate,votes in counts.items():

            if votes > total/2:

                return {

                    "winner":candidate,

                    "rounds":rounds,

                    "first_preferences":rounds[0],

                    "final_count":dict(counts),

                    "flows":flows

                }





        eliminated=min(

            active,

            key=lambda c:counts.get(c,0)

        )


        active.remove(eliminated)



        transfers=Counter()



        for ballot in ballots:

            if eliminated in ballot:

                index=ballot.index(eliminated)


                for preference in ballot[index+1:]:

                    if preference in active:

                        transfers[preference]+=1
                        break



        for destination,votes in transfers.items():

            flows.append({

                "from":eliminated,

                "to":destination,

                "votes":votes

            })







# ==========================
# RUN ALL ELECTIONS
# ==========================


candidates = load_candidates()

ballots = load_ballots()

previous = load_previous()


results={}



for role in ballots:


    result=count_election(
        ballots[role]
    )


    total=sum(
        result["first_preferences"].values()
    )


    first_percent={

        c:round(v/total*100,2)

        for c,v in result["first_preferences"].items()

    }



    swing={}


    for candidate,old in previous[role].items():

        if candidate in first_percent:

            swing[candidate]=round(

                first_percent[candidate]-old,

                2

            )





    results[role]={

        "winner":result["winner"],

        "candidates":candidates[role],

        "first_preferences":
        result["first_preferences"],

        "first_percent":
        first_percent,

        "final_count":
        result["final_count"],

        "swing":
        swing,

        "rounds":
        result["rounds"],

        "flows":
        result["flows"]

    }





# ==========================
# EXPORT
# ==========================


with open(
    "results.json",
    "w"
) as file:

    json.dump(
        results,
        file,
        indent=4
    )


print("Election completed!")

for role,data in results.items():

    print(
        role,
        "→",
        data["winner"]
    )
