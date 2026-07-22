/* ============================================================================
   Application Request Management System
   Database: Microsoft SQL Server 2017+
   File: schema_sqlserver.sql
   Purpose: Creates all tables, keys, constraints and indexes described in
            Section 4 (Database Design) of the Application Design Pack.
   ============================================================================ */

IF DB_ID('kiosk') IS NULL
BEGIN
    CREATE DATABASE kiosk;
END
GO

USE kiosk;
GO

/* ---------------------------------------------------------------------------
   1. ROLES
   RoleID(PK), RoleName
   --------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.ChangeFlowRoles', 'U') IS NOT NULL DROP TABLE dbo.ChangeFlowRoles;
GO
CREATE TABLE dbo.ChangeFlowRoles (
    RoleID      INT IDENTITY(1,1) PRIMARY KEY,
    RoleName    VARCHAR(50) NOT NULL UNIQUE
        CHECK (RoleName IN ('Requester','Platform Owner','PGC','Developer','Admin'))
);
GO

/* ---------------------------------------------------------------------------
   2. BUSINESS
   --------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.ChangeFlowBusiness', 'U') IS NOT NULL
    DROP TABLE dbo.ChangeFlowBusiness;
GO

CREATE TABLE dbo.ChangeFlowBusiness
(
    BusinessID     INT IDENTITY(1,1) PRIMARY KEY,
    BusinessName   VARCHAR(100) NOT NULL UNIQUE,
    IsActive       BIT DEFAULT 1
);
GO


/* ---------------------------------------------------------------------------
   2. PLATFORMS
   PlatformID(PK), PlatformName, OwnerID
   --------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.ChangeFlowPlatforms', 'U') IS NOT NULL DROP TABLE dbo.ChangeFlowPlatforms;
GO
CREATE TABLE dbo.ChangeFlowPlatforms (
    PlatformID      INT IDENTITY(1,1) PRIMARY KEY,
    PlatformName    VARCHAR(150) NOT NULL UNIQUE,
    OwnerID         INT NULL,         -- FK to Users.UserID, added after Users exists
    IsActive        BIT NOT NULL DEFAULT 1
);
GO

/* ---------------------------------------------------------------------------
   3. USERS
   UserID(PK), Name, Email, RoleID, PlatformID, Status
   --------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.ChangeFlowUsers', 'U') IS NOT NULL DROP TABLE dbo.ChangeFlowUsers;
GO
CREATE TABLE dbo.ChangeFlowUsers (
    UserID          INT IDENTITY(1,1) PRIMARY KEY,
    Name            VARCHAR(150) NOT NULL,
    Email           VARCHAR(150) NOT NULL UNIQUE,
    PasswordHash    VARCHAR(255) NOT NULL,
    RoleID          INT NOT NULL,
    PlatformID      INT NULL,          -- Platform the user belongs to / owns (nullable for Admin/PGC)
    BusinessID      INT NULL,          -- NEW
    Status          VARCHAR(20) NOT NULL DEFAULT 'Active'
        CHECK (Status IN ('Active','Inactive')),
    CreatedDate     DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_Users_Roles     FOREIGN KEY (RoleID)     REFERENCES dbo.ChangeFlowRoles(RoleID),
    CONSTRAINT FK_Users_Platforms FOREIGN KEY (PlatformID) REFERENCES dbo.ChangeFlowPlatforms(PlatformID),
    CONSTRAINT FK_Users_Business FOREIGN KEY (BusinessID) REFERENCES dbo.ChangeFlowBusiness(BusinessID)
);
GO

-- Now that Users exists, wire up Platforms.OwnerID
ALTER TABLE dbo.ChangeFlowPlatforms
    ADD CONSTRAINT FK_Platforms_Owner FOREIGN KEY (OwnerID) REFERENCES dbo.ChangeFlowUsers(UserID);
GO

/* ---------------------------------------------------------------------------
   4. CATEGORIES  (supports Admin Masters screen: Platform / Users / Categories)
   --------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.ChangeFlowCategories', 'U') IS NOT NULL DROP TABLE dbo.ChangeFlowCategories;
GO
CREATE TABLE dbo.ChangeFlowCategories (
    CategoryID      INT IDENTITY(1,1) PRIMARY KEY,
    CategoryName    VARCHAR(100) NOT NULL UNIQUE,
    Type            VARCHAR(20) NOT NULL DEFAULT 'Enhancement'
        CHECK (Type IN ('Project','Enhancement')),
    IsActive        BIT NOT NULL DEFAULT 1
);
GO

/* ---------------------------------------------------------------------------
   5. REQUESTS
   RequestID(PK), Type, PlatformID, RequesterID, Priority, Description,
   Status, CreatedDate
   --------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.ChangeFlowRequests', 'U') IS NOT NULL DROP TABLE dbo.ChangeFlowRequests;
GO
CREATE TABLE dbo.ChangeFlowRequests (
    RequestID       INT IDENTITY(1,1) PRIMARY KEY,
    Type            VARCHAR(20) NOT NULL
        CHECK (Type IN ('Project','Enhancement')),
    PlatformID      INT NOT NULL,
    CategoryID      INT NULL,
    RequesterID     INT NOT NULL,
    Priority        VARCHAR(20) NOT NULL
        CHECK (Priority IN ('Low','Medium','High','Critical')),
    Description     VARCHAR(2000) NOT NULL,
    AttachmentPath  VARCHAR(500) NULL,
    Status          VARCHAR(40) NOT NULL DEFAULT 'Pending Platform Approval'
        CHECK (Status IN (
            'Pending Platform Approval','Pending PGC Approval',
            'In Development','Testing/UAT','Production','Closed','Rejected')),
    CreatedDate     DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_Requests_Platforms  FOREIGN KEY (PlatformID)  REFERENCES dbo.ChangeFlowPlatforms(PlatformID),
    CONSTRAINT FK_Requests_Categories FOREIGN KEY (CategoryID) REFERENCES dbo.ChangeFlowCategories(CategoryID),
    CONSTRAINT FK_Requests_Requester  FOREIGN KEY (RequesterID) REFERENCES dbo.ChangeFlowUsers(UserID)
);
GO
CREATE INDEX IX_Requests_Status     ON dbo.ChangeFlowRequests(Status);
CREATE INDEX IX_Requests_PlatformID ON dbo.ChangeFlowRequests(PlatformID);
CREATE INDEX IX_Requests_RequesterID ON dbo.ChangeFlowRequests(RequesterID);
GO

/* ---------------------------------------------------------------------------
   6. APPROVALS
   ApprovalID(PK), RequestID, Level, ApproverID, Decision, Remarks, Date
   --------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.ChangeFlowApprovals', 'U') IS NOT NULL DROP TABLE dbo.ChangeFlowApprovals;
GO
CREATE TABLE dbo.ChangeFlowApprovals (
    ApprovalID      INT IDENTITY(1,1) PRIMARY KEY,
    RequestID       INT NOT NULL,
    Level           VARCHAR(20) NOT NULL
        CHECK (Level IN ('Platform Owner','PGC')),
    ApproverID      INT NOT NULL,
    Decision        VARCHAR(20) NOT NULL DEFAULT 'Pending'
        CHECK (Decision IN ('Pending','Approved','Rejected')),
    Remarks         VARCHAR(1000) NULL,
    Date            DATETIME2 NULL,
    CONSTRAINT FK_Approvals_Requests FOREIGN KEY (RequestID)  REFERENCES dbo.ChangeFlowRequests(RequestID) ON DELETE CASCADE,
    CONSTRAINT FK_Approvals_Approver FOREIGN KEY (ApproverID) REFERENCES dbo.ChangeFlowUsers(UserID)
);
GO
CREATE INDEX IX_Approvals_RequestID ON dbo.ChangeFlowApprovals(RequestID);
GO

/* ---------------------------------------------------------------------------
   7. DEVELOPMENT
   DevID(PK), RequestID, AssignedTo, StartDate, TargetDate, CompletionDate,
   Progress
   --------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.ChangeFlowDevelopment', 'U') IS NOT NULL DROP TABLE dbo.ChangeFlowDevelopment;
GO
CREATE TABLE dbo.ChangeFlowDevelopment (
    DevID           INT IDENTITY(1,1) PRIMARY KEY,
    RequestID       INT NOT NULL UNIQUE,
    AssignedTo      INT NULL,
    StartDate       DATE NULL,
    TargetDate      DATE NULL,
    CompletionDate  DATE NULL,
    Progress        TINYINT NOT NULL DEFAULT 0 CHECK (Progress BETWEEN 0 AND 100),
    CONSTRAINT FK_Development_Requests FOREIGN KEY (RequestID)  REFERENCES dbo.ChangeFlowRequests(RequestID) ON DELETE CASCADE,
    CONSTRAINT FK_Development_Assignee FOREIGN KEY (AssignedTo) REFERENCES dbo.ChangeFlowUsers(UserID)
);
GO
CREATE INDEX IX_Development_AssignedTo ON dbo.ChangeFlowDevelopment(AssignedTo);
GO

/* ---------------------------------------------------------------------------
   8. AUDIT / ACTIVITY LOG (feeds "Recent Activities" dashboard widget)
   --------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.ChangeFlowActivityLog', 'U') IS NOT NULL DROP TABLE dbo.ChangeFlowActivityLog;
GO
CREATE TABLE dbo.ChangeFlowActivityLog (
    ActivityID      INT IDENTITY(1,1) PRIMARY KEY,
    RequestID       INT NULL,
    UserID          INT NULL,
    Action          VARCHAR(200) NOT NULL,
    Timestamp       DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_Activity_Requests FOREIGN KEY (RequestID) REFERENCES dbo.ChangeFlowRequests(RequestID) ON DELETE CASCADE,
    CONSTRAINT FK_Activity_Users    FOREIGN KEY (UserID)    REFERENCES dbo.ChangeFlowUsers(UserID)
);
GO

PRINT 'Schema created successfully.';
