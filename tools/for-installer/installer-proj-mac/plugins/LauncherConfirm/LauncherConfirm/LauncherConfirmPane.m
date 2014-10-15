//
//  LauncherConfirmPane.m
//  LauncherConfirm
//
//  Created by zhangbin on 14-10-11.
//  Copyright (c) 2014年 cocos2d-x. All rights reserved.
//

#import "LauncherConfirmPane.h"

@implementation LauncherConfirmPane

NSString* launcherPath = @"/Applications/cocos/Cocos.app";

- (void)didEnterPane:(InstallerSectionDirection)aDir
{
    NSDate * now = [NSDate date];
    NSDateFormatter *fmt = [[NSDateFormatter alloc] init];
    fmt.dateStyle = kCFDateFormatterMediumStyle;
    fmt.timeStyle = kCFDateFormatterShortStyle;
    NSString *newDateString = [fmt stringFromDate:now];
    [self installLog:""];
    [self installLog:[newDateString UTF8String]];
}

- (void)willExitPane:(InstallerSectionDirection)aDir
{
    [self installLog:"will exit pane invoked!"];
    if ([btnLaunch state] == NSOnState) {
        [self installLog:"button state is ON!"];
        BOOL bRet = [[NSWorkspace sharedWorkspace] openFile:launcherPath];
        if (bRet) {
            [self installLog:"launch OK"];
        }
        else
        {
            [self installLog:"launch failed"];
        }
    }
}

- (BOOL)shouldExitPane:(InstallerSectionDirection)aDir
{
    [self installLog:"should exit pane invoked!"];
    return YES;
}

- (NSString *)title
{
	return [[NSBundle bundleForClass:[self class]] localizedStringForKey:@"PaneTitle" value:nil table:nil];
}

- (const char*) getLogFilePath
{
    NSString* homePath = NSHomeDirectory();
    NSString* retPath = [NSString stringWithFormat:@"%@/.cocos2d", homePath];
    NSString* retFilePath = [NSString stringWithFormat:@"%@/install-log.txt", retPath];
    NSFileManager* fileManager = [NSFileManager defaultManager];
    if (! [fileManager fileExistsAtPath:retFilePath]) {
        [fileManager createDirectoryAtPath:retPath withIntermediateDirectories:YES attributes:nil error:nil];
        [fileManager createFileAtPath:retFilePath contents:nil attributes:nil];
    }
    
    return [retFilePath UTF8String];
}

- (void) installLog:(const char *) format,...
{
    va_list list;
    va_start(list, format);
    
    char buf[1024];
    vsnprintf(buf, 1021, format, list);
    strcat(buf, "\n");
    
    FILE *fp = fopen([self getLogFilePath],"a");
    fprintf(fp, "%s", buf);
    fclose(fp);
    
    va_end(list);
}

@end
