define i32 @max(i32 %a, i32 %b) {
entry:
  %0 = icmp sgt i32 %a, %b
  br i1 %0, label %btrue, label %bfalse

btrue:                                      
  br label %end

bfalse:                                    
  br label %end

end:                                   
  %retval = phi i32 [%a, %btrue], [%b, %bfalse]
  ret i32 %retval
}
