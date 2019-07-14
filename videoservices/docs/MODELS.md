Model Architecture Planning

Membership

    -slug    
    -type (free,pro,enterprise)
    -price
    -stripe plan id
    
UserMembership

    -user   (foreign key to default user)
    -stripe customer id
    -membership type (foreign key to Membership)
    
Subscription

    -user membership
    -stripe subscription id (foreign key to user membership)
    -active

Course
    
    -slug
    -title
    -description
    -allowed membership (foreign key to membership)
    
Lesson

    -slug
    -title
    -course (foreign key to Course)
    -description
    -video
    -thumbnail