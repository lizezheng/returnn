
funloader_support_code = """
#include <sstream>
#include <vector>

void printPyObj(PyObject * o)
{
  PyObject* objectsRepresentation = PyObject_Repr(o);
  const char* s = PyString_AsString(objectsRepresentation);
  std::cout << s << std::endl;
  Py_DECREF(objectsRepresentation);
}

struct FunLoader
{
  PyObject * fn;
  PyObject * reset_fn;
  PyObject * mod;
  std::vector<PyObject*> res_shared;
  std::string name;

  FunLoader(const char * fn_name, const char * reset_fn_name = 0)
  {
    std::cout << "Loading function " << fn_name << "..." << std::endl;
    name = fn_name;
    mod = PyImport_ImportModule("CustomLSTMFunctions");
    assert(mod);
    fn = PyObject_GetAttrString(mod, fn_name);
    if(reset_fn_name)
    {
      reset_fn = PyObject_GetAttrString(mod, reset_fn_name);
    }
    else
    {
      reset_fn = 0;
    }
    std::stringstream ss0;
    ss0 << fn_name << "_res0";
    std::stringstream ss1;
    ss1 << fn_name << "_res1";
    PyObject * res0 = PyObject_GetAttrString(mod, ss0.str().c_str());
    PyObject * res1 = PyObject_GetAttrString(mod, ss1.str().c_str());
    res_shared.push_back(res0);
    assert(PyList_Check(res1));
    int len = PyList_Size(res1);
    for(int i = 0; i < len; ++i)
    {
      PyObject* obj = PyList_GetItem(res1, i);
      Py_XINCREF(obj);
      res_shared.push_back(obj);
    }

    std::cout << "loaded function" << std::endl;
  }

  ~FunLoader()
  {
    Py_XDECREF(fn);
    Py_XDECREF(reset_fn);
    for(int i = 0; i < res_shared.size(); ++i)
    {
      Py_XDECREF(res_shared[i]);
    }
    Py_DECREF(mod);
  }

  void reset_shared()
  {
    assert(reset_fn);
    PyObject_CallObject(reset_fn, 0);
  }

  void reset_shared(CudaNdarray * x0)
  {
    assert(reset_fn);
    PyObject* args = PyTuple_Pack(1, x0);
    PyObject_CallObject(reset_fn, args);
    Py_DECREF(args);
  }

  void reset_shared(CudaNdarray * x0, CudaNdarray * x1)
  {
    assert(reset_fn);
    PyObject* args = PyTuple_Pack(2, x0, x1);
    PyObject_CallObject(reset_fn, args);
    Py_DECREF(args);
  }

  void reset_shared(CudaNdarray * x0, CudaNdarray * x1, CudaNdarray * x2)
  {
    assert(reset_fn);
    PyObject* args = PyTuple_Pack(3, x0, x1, x2);
    PyObject_CallObject(reset_fn, args);
    Py_DECREF(args);
  }

  void reset_shared(CudaNdarray * x0, CudaNdarray * x1, CudaNdarray * x2, CudaNdarray * x3)
  {
    assert(reset_fn);
    PyObject* args = PyTuple_Pack(4, x0, x1, x2, x3);
    PyObject_CallObject(reset_fn, args);
    Py_DECREF(args);
  }

  void reset_shared(CudaNdarray * x0, CudaNdarray * x1, CudaNdarray * x2, CudaNdarray * x3, CudaNdarray * x4)
  {
    assert(reset_fn);
    PyObject* args = PyTuple_Pack(5, x0, x1, x2, x3, x4);
    PyObject_CallObject(reset_fn, args);
    Py_DECREF(args);
  }

  std::vector<CudaNdarray*> call_helper(PyObject * args)
  {
    //std::cout << "calling custom function " << name << "..." << std::endl;
    PyObject_CallObject(fn, args);
    Py_DECREF(args);

    std::vector<CudaNdarray*> res;
    for(int i = 0; i < res_shared.size(); ++i)
    {
      //res_shared.get_value(borrow=True, return_internal_type=True)
      PyObject * sub_res = PyObject_CallMethod(res_shared[i], "get_value", "(ii)", 1, 1);
      assert(sub_res);
      res.push_back((CudaNdarray*) sub_res);
    }
    //std::cout << "custom function finished" << std::endl;
    return res;
  }

  std::vector<CudaNdarray*> operator()(CudaNdarray* x)
  {
    PyObject* args = PyTuple_Pack(1, x);
    return call_helper(args);
  }

  std::vector<CudaNdarray*> operator()(CudaNdarray* x, CudaNdarray* y)
  {
    PyObject* args = PyTuple_Pack(2, x, y);
    return call_helper(args);
  }

  std::vector<CudaNdarray*> operator()(CudaNdarray* x, CudaNdarray* y, CudaNdarray* z)
  {
    PyObject* args = PyTuple_Pack(3, x, y, z);
    return call_helper(args);
  }

  std::vector<CudaNdarray*> operator()(CudaNdarray* x0, CudaNdarray* x1, CudaNdarray* x2, CudaNdarray* x3)
  {
    PyObject* args = PyTuple_Pack(4, x0, x1, x2, x3);
    return call_helper(args);
  }

  std::vector<CudaNdarray*> operator()(CudaNdarray* x0, CudaNdarray* x1, CudaNdarray* x2, CudaNdarray* x3, CudaNdarray* x4)
  {
    PyObject* args = PyTuple_Pack(5, x0, x1, x2, x3, x4);
    return call_helper(args);
  }

  //TODO add overloads for more arguments if needed
  //(variadic template would be better but not widely supported by compilers)

};

"""

def make_funloader_code(fn_name, reset_fn_name=None):
  if reset_fn_name is not None:
    return funloader_support_code + """
    FunLoader %(fn_name)s("%(fn_name)s", "%(reset_fn_name)s");
    """ % locals()
  else:
    return funloader_support_code + """
    FunLoader %(fn_name)s("%(fn_name)s", 0);
    """ % locals()
