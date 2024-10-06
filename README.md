Numpy


```python
import numpy as np
arr = np.array([1, 2, 3, 4])
print(arr)
```

    [1 2 3 4]



```python
# construct a 2d array
arr_2d = np.array([[1, 2, 3], [4, 5, 6]])
print(arr_2d)
```

    [[1 2 3]
     [4 5 6]]



```python
# construct a 3d array
arr_3d = np.array([[[1, 2, 3],
          [4, 5, 6]],
           [[7, 8, 9],
          [10, 11, 12]],
           [[13, 14, 15],
          [16, 17, 18]]])

print(arr_3d)
```

    [[[ 1  2  3]
      [ 4  5  6]]
    
     [[ 7  8  9]
      [10 11 12]]
    
     [[13 14 15]
      [16 17 18]]]



```python
arr = np.zeros((3, 3))
print(arr)
```

    [[0. 0. 0.]
     [0. 0. 0.]
     [0. 0. 0.]]



```python
arr = np.ones((2, 4))
print(arr)
```

    [[1. 1. 1. 1.]
     [1. 1. 1. 1.]]



```python
arr = np.ones((2, 4))
print(arr)
arr.shape

```

    [[1. 1. 1. 1.]
     [1. 1. 1. 1.]]





    (2, 4)




```python
arr_2d = np.array([[1, 2, 3], [4, 5, 6]])
arr_2d.size
```




    6




```python
# get element from array by index
arr = np.array([1, 2, 3, 4])
arr[1]

```




    2




```python
# get element from array by index
arr_2d = np.array([[1, 2, 3], [4, 5, 6]])
print(arr_2d[0])
print(arr_2d[0][1])
```

    [1 2 3]
    2



```python
arr = np.array([1, 2, 3, 4])
reshaped_arr = arr.reshape((2, 2))
print(arr)
print('-----------')
print(reshaped_arr)


```

    [1 2 3 4]
    -----------
    [[1 2]
     [3 4]]



```python
arr = np.array([1, 2, 3, 4])
reshaped_arr = arr.reshape((2, 2))

reshaped_back_arr = reshaped_arr.reshape(-1)
print(arr)
print('-----------')
print(reshaped_arr)
print('-----------')
print(reshaped_back_arr)
```

    [1 2 3 4]
    -----------
    [[1 2]
     [3 4]]
    -----------
    [1 2 3 4]



```python
arr1 = np.ones((3,3))
arr2 = np.eye(3)

arr = arr1 + arr2
print(arr1)
print('==============')
print(arr2)
print('==============')
print(arr)
```

    [[1. 1. 1.]
     [1. 1. 1.]
     [1. 1. 1.]]
    ==============
    [[1. 0. 0.]
     [0. 1. 0.]
     [0. 0. 1.]]
    ==============
    [[2. 1. 1.]
     [1. 2. 1.]
     [1. 1. 2.]]



```python
arr1 = np.array([2,4])
arr = arr1 + 5

print(arr1)
print('==============')
print(arr)
```

    [2 4]
    ==============
    [7 9]



```python
arr1 = np.arange(0, 6).reshape(2,3)
arr2 = np.array([2,2,2])
arr = arr1 * arr2
print(arr1)
print('==============')
print(arr2)
print('==============')
print(arr)
```

    [[0 1 2]
     [3 4 5]]
    ==============
    [2 2 2]
    ==============
    [[ 0  2  4]
     [ 6  8 10]]



```python
arr1 = np.arange(0, 6).reshape(2,3)
arr2 = np.array([[2],[2]])
arr = arr1 * arr2
print(arr1)
print('==============')
print(arr2)
print('==============')
print(arr)
```

    [[0 1 2]
     [3 4 5]]
    ==============
    [[2]
     [2]]
    ==============
    [[ 0  2  4]
     [ 6  8 10]]



```python
a = np.array([[1,2,3],[4,8,16]])
b = np.array([5,6,11]).reshape(-1,1)
c = np.dot(a,b)
print(a)
print('shape of a is:', a.shape)
print('==============')
print(b)
print('shape of b is:', b.shape)
print('==============')
print(c)
print('shape of c is:', c.shape)
```

    [[ 1  2  3]
     [ 4  8 16]]
    shape of a is: (2, 3)
    ==============
    [[ 5]
     [ 6]
     [11]]
    shape of b is: (3, 1)
    ==============
    [[ 50]
     [244]]
    shape of c is: (2, 1)



```python
a = np.array([[1,2,3],[4,8,16]])
b = np.array([5,6,11]).reshape(-1,1)
c = np.matmul(a,b)
print(a)
print('shape of a is:', a.shape)
print('==============')
print(b)
print('shape of b is:', b.shape)
print('==============')
print(c)
print('shape of c is:', c.shape)
```

    [[ 1  2  3]
     [ 4  8 16]]
    shape of a is: (2, 3)
    ==============
    [[ 5]
     [ 6]
     [11]]
    shape of b is: (3, 1)
    ==============
    [[ 50]
     [244]]
    shape of c is: (2, 1)

