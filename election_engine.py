import csv
import json
from collections import Counter, defaultdict


def load_candidates():

    candidates = {}

    with open("data/candidates.csv") as file:

        reader = csv.DictReader(file)

        for row in reader:

            candidates[row["candidate"]] = {
                "party": row["party"],
                "colour": row["colour"]
            }

    return candidates



def load_ballots():

    ballots = defaultdict(list)

    with open("data/current_ballots.csv") as file:

        reader = csv.DictReader(file)

        for row in reader:

            prefs=[]

            for key,value in row.items():

                if key.startswith("pref") and value:
                    prefs.append(value)

            ballots[row["role"]].append(prefs)

    return ballots



def load_previous():

    previous=defaultdict(dict)

    with open("data/previous_results.csv") as file:

        reader=csv.DictReader(file)

        for row in reader:

            previous[row["role"]][row["candidate"]] = {
                "primary":float(row["first_preference_percent"]),
                "two_pp":float(row["two_candidate_percent"])
            }

    return previous





def count_election(ballots):

    candidates=[]

    for ballot in ballots:

        for candidate in ballot:

            if candidate not in candidates:
                candidates.append(candidate)



    active=candidates.copy()

    counts_history=[]



    while True:


        counts=Counter()


        for ballot in ballots:

            for preference in ballot:

                if preference in active:

                    counts[preference]+=1
                    break



        total=sum(counts.values())


        counts_history.append({

            candidate:{
                "votes":votes,
                "percent":round(votes/total*100,2)
            }

            for candidate,votes in counts.items()

        })



        for candidate,votes in counts.items():

            if votes > total/2:

                return {

                    "winner":candidate,
                    "history":counts_history,
                    "final":dict(counts)

                }



        eliminated=min(
            active,
            key=lambda x:counts.get(x,0)
        )


        active.remove(eliminated)







candidates=load_candidates()

ballots=load_ballots()

previous=load_previous()


results={}



for role,role_ballots in ballots.items():


    result=count_election(role_ballots)


    first=result["history"][0]


    first_percent={

        name:data["percent"]

        for name,data in first.items()

    }



    # primary swings

    primary_swing={}



    for candidate,value in first_percent.items():

        if candidate in previous[role]:

            primary_swing[candidate]=round(

                value -
                previous[role][candidate]["primary"],

                2

            )




    # 2PP calculation

    final=result["final"]

    total=sum(final.values())


    final_percent={

        name:round(votes/total*100,2)

        for name,votes in final.items()

    }



    winner=result["winner"]



    previous_2pp = previous[role].get(
        winner,
        {}
    ).get(
        "two_pp",
        None
    )



    if previous_2pp is not None:

        two_pp_swing=round(

            final_percent[winner]-previous_2pp,

            2

        )

    else:

        two_pp_swing=None






    candidate_data={}


    for candidate in first_percent:


        info=candidates.get(
            candidate,
            {}
        )


        candidate_data[candidate]={

            "party":
            info.get("party","Independent"),


            "colour":
            info.get("colour","#64748b"),


            "incumbent":
            candidate in previous[role]

        }





    results[role]={

        "winner":winner,

        "candidates":candidate_data,


        "first_percent":
        first_percent,


        "primary_swing":
        primary_swing,


        "two_pp":
        final_percent,


        "two_pp_swing":
        two_pp_swing,


        "history":
        result["history"]

    }





with open("results.json","w") as file:

    json.dump(
        results,
        file,
        indent=4
    )


print("Election complete!")

for role,result in results.items():

    print(
        role,
        "→",
        result["winner"]
    )
