def group_numbers(lst, target_sum):
    lst.sort(reverse=True)
    sublists = []

    for num in lst:
        for sublist in sublists:
            if sum(sublist) + num <= target_sum:
                sublist.append(num)
                break
        else:
            # If no sublist could accommodate num, start a new one
            sublists.append([num])

    return sublists


lst = [1,1,1,2,2,2,3,3,3,10,20,13,8,7,5,3,4,3,3,5,11]
target_sum = 10

sorted = group_numbers(lst, target_sum)

print(sorted)
