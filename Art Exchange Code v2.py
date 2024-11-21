import pandas as pd
import random

# ==================================================
# CSV Parsing Utilities
# ==================================================

def commas_to_set(raw):
    if isinstance(raw, float):
        # Empty column is typed as NAN float
        return {}
    return {x.strip() for x in raw.split(',')}

class Artist:
    '''
    Art Exchange CSV format:
    Columns: 
    0. Name
    1. Discord
    2. Email
    3. Wishlist
    4. Wishlist Tags
    5. Blacklist Tags
    6. References
    '''
    def __init__(self, row):
        self.name = row.iloc[0]
        self.discord = row.iloc[1]
        self.email = row.iloc[2]
        self.wishlist = row.iloc[3]
        self.wishlist_tags = commas_to_set(row.iloc[4])
        self.blacklist_tags = commas_to_set(row.iloc[5])
        self.references = row.iloc[6]
        self.dataframe = row
    
    def __repr__(self):
        return str(self.__dict__)
    
# ==================================================
# Main Function
# ==================================================

def main():
    NUM_ATTEMPTS = 100
    csvraw = pd.read_csv('input.csv')
    raw = [x[1] for x in csvraw.iterrows()]
    artists = [Artist(x) for x in raw]

    success = False
    final_output = None
    for _ in range(NUM_ATTEMPTS):
        result = run(artists)
        if result['success']:
            final_output = result
            success = True
            break
    
    if success:
        print('SUCCESS')
        assignments = final_output['assignments']
        print_assignments(assignments)
        export_to_csv(assignments)
    else:
        print('FAILED')
        print(f'Could not match after {NUM_ATTEMPTS} attempts')

# ==================================================
# Matching Algorithm
# ==================================================

def run(artists):
    assignments = []
    failed = []
    available = artists.copy()

    # Expecting that shuffling list will add enough randomness to assignment
    # process to magically find a fit, increase number of attempts if frequently
    # fails to find match
    #
    # Some datasets simply are not possible to match, in which case, 
    # if the number of attempts is very high and there is still not a match,
    # check the actual wishlists and blacklists to trying and find an opening
    random.shuffle(available)

    for request in artists:
        for i in range(len(available)):
            option = available[i]

            if request.discord == option.discord:
                # Requestor and artist is same person, 
                pass

            # If the REQUESTOR wishlist tags are not in ARTIST blacklist tags
            # AND not already taken, assign and drop
            if request.wishlist_tags.isdisjoint(option.blacklist_tags):
                # The request did not hit anything in the blacklist
                assignments.append((request, option))
                available.pop(i)
                break
        else:
            # If else block executes, iterated over entire option list without
            # finding a match. Put this artist into the failed match list for
            # future reference
            failed.append(request)
    
    output = {
        'success': len(failed) == 0,
        'assignments': assignments,
        'failed': failed,
    }

    return output

# ==================================================
# Print Outs and Export
# ==================================================
            
def print_assignments(assignments):
    print('--- Assignments ---')
    print('Requestor -> Artist')
    print()
    for (req, asgn) in assignments:
        print(f'{req.name} -> {asgn.name}')

'''
    Creates a data frame from a list of records

    Input (python types):
        list_of_records = [
            ('one', '1'),
            ('two', '2'),
            ('three', '3'),
        ]
        column_names = ['text', 'value']

    Output (csv equivalent):
        text,value
        one,1
        two,2
        three,3
'''
def create_dataframe(column_names, list_of_records):
    return pd.DataFrame.from_records(list_of_records, columns=column_names)

# artist, artist tag, requestor, wishlist, references
def export_to_csv(assignments):
    headers = ['Requestor Name', 'Requestor Discord', 'Assignee Name', 'Assignee Discord', 'Prompt', 'References', 'Intro Message']
    records = []
    for requestor, assignee in assignments:
        intromessage = f'''Hello {assignee.name}! You've been assigned {requestor.name}'s request. Here is the prompt: {requestor.wishlist}. 
        Here are the provided reference pics: {requestor.references}. The first check-in will be on **Saturday November 30th**
        Art will be due by **Sat Dec 21st Midnight**. Let us know if you have any questions, good luck and have fun! '''
        r = (requestor.name, requestor.discord, assignee.name, assignee.discord, requestor.wishlist, requestor.references, intromessage)
        records.append(r)

    df = create_dataframe(headers, records)
    df.to_csv('output.csv', sep=',', index=False, encoding='utf-8')

# ==================================================
# Execution Guard
# ==================================================

if __name__ == '__main__':
    main()