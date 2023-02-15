def find_differences(list1, list2):
    """
    Takes two lists as input and returns a new list containing the elements that are different between them.
    """
    # create an empty list to store the differences
    differences = []
    
    # iterate over the elements in list1
    for element in list1:
        # if the element is not in list2, add it to the differences list
        if element not in list2:
            differences.append(element)
    
    # iterate over the elements in list2
    # for element in list2:
    #     # if the element is not in list1, add it to the differences list
    #     if element not in list1:
    #         differences.append(element)
    
    # return the differences list
    return differences