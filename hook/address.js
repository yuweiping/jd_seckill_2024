//http://91fans.com.cn/post/ldqsignfour/

var StrCls = Java.use('java.lang.String');

var desCbcCls = Java.use('com.jd.jdsdk.security.DesCbcCrypto');
desCbcCls.encrypt.overload('java.lang.String','java.lang.String','[B','java.lang.String').implementation = function(a,b,c,d){
        var result = this.encrypt(a,b,c);

        console.log("### encrypt  原文=" + a + ",密钥=" + b + ",d=" + d);
        console.log("rc=" + bytesToBase64(result));
        return result;
}

desCbcCls.decrypt.overload('java.lang.String','java.lang.String','[B').implementation = function(a,b,c){
        var result = this.decrypt(a,b,c);
        console.log("### decrypt  密文=" + a + ",密钥=" + b);
        console.log("rc=" + StrCls.$new(result));
        return result;
}