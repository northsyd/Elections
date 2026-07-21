import csv
import json
from collections import Counter, defaultdict


# ==========================
# LOAD CSV FILES
# ==========================


def load_candidates():

    candidates = {}

    with open("data/candidates.csv", newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:

            candidates[row["candidate"]] = {

                "party": row["party"],

                "colour": row["colour"]

            }

    return candidates



def load_ballots():

    ballots = defaultdict(list)

    with open("data/current_ballots.csv", newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:

            preferences = []

            for key,value in row.items():

                if key.startswith("pref") and value:

                    preferences.append(value)


            ballots[row["role"]].append(preferences)


    return ballots



def load_previous():

    previous = defaultdict(dict)

    with open("data/previous_results.csv", newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:

            previous[row["role"]][row["candidate"]] = float(
                row["first_preference_percent"]
            )

    return previous





# ==========================
# PREFERENTIAL COUNT
# ==========================


def run_count(ballots):

    candidates = []

    for ballot in ballots:

        for candidate in ballot:

            if candidate not in candidates:

                candidates.append(candidate)


    active = candidates.copy()

    rounds=[]

    flows=[]



    while True:


        counts = Counter()


        for ballot in ballots:

            for candidate in ballot:

                if candidate in active:

                    counts[candidate]+=1

                    break



        rounds.append(dict(counts))


        total=sum(counts.values())



        # winner

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

            key=lambda c: counts.get(c,0)

        )


        active.remove(eliminated)



        transfers=Counter()



        for ballot in ballots:


            if eliminated in ballot:


                position=ballot.index(eliminated)



                for preference in ballot[position+1:]:


                    if preference in active:

                        transfers[preference]+=1

                        break



        for target,votes in transfers.items():

            flows.append({

                "from": eliminated,

                "to": target,

                "votes": votes

            })







# ==========================
# BUILD RESULTS
# ==========================


candidate_info = load_candidates()

ballots = load_ballots()

previous = load_previous()



results={}



for role,role_ballots in ballots.items():


    result = run_count(role_ballots)



    first = result["first_preferences"]


    total=sum(first.values())



    first_percent={

        candidate:
        round(votes/total*100,2)

        for candidate,votes in first.items()

    }



    swing={}



    for candidate,old in previous[role].items():

        if candidate in first_percent:

            swing[candidate]=round(

                first_percent[candidate]-old,

                2

            )





    # attach candidate data

    candidates={}



    for candidate in first_percent:


        info = candidate_info.get(

            candidate,

            {}

        )


        candidates[candidate]={

            "party":info.get(
                "party",
                "Independent"
            ),


            "colour":info.get(
                "colour",
                "#64748b"
            ),


            # incumbent for this role only

            "incumbent":
            candidate in previous[role]

        }





    results[role]={


        "winner":result["winner"],


        "candidates":candidates,


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


with open("results.json","w") as file:

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
