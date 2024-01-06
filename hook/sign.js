function HookHandle(clazz) {
  clazz.getSignFromJni.implementation = function (a, b, c, d, e, f) {
    var r = this.getSignFromJni(a, b, c, d, e, f)
    console.log('=======================================')
    console.log('param1: ', a)
    console.log('param2: ', b)
    console.log('param3: ', c)
    console.log('param4: ', d)
    console.log('param5: ', e)
    console.log('param6: ', f)
    console.log('result: ', r)
    return r
  }
  console.log('HookHandle ok')
}

Java.perform(function () {
  Java.choose('dalvik.system.PathClassLoader', {
    onMatch: function (instance) {
      try {
        var clazz = Java.use('com.jingdong.common.utils.BitmapkitUtils')
        HookHandle(clazz)

        return 'stop'
      } catch (e) {
        console.log('next')
        console.log(e)
      }
    },
    onComplete: function () {
      console.log('success')
    },
  })
})
