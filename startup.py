# -*- coding: utf-8 -*-
"""
pyRevit Startup Script for Riyan Plugin
Checks for updates on GitHub and notifies the user.
"""
import ssl
import json
import urllib2
import os
import System
import subprocess
from pyrevit import forms
from System.Windows.Markup import XamlReader
from System.Windows.Media.Imaging import BitmapImage
from System import Uri, UriKind

def check_for_updates():
    try:
        # Get local commit hash
        plugin_dir = os.path.dirname(__file__)
        head_file = os.path.join(plugin_dir, ".git", "refs", "heads", "main")
        
        if not os.path.exists(head_file):
            return
            
        with open(head_file, "r") as f:
            local_commit = f.read().strip()
            
        # Get remote commit hash from GitHub API
        url = "https://api.github.com/repos/udarieimalsha/TestRiyanPlugin/commits/main"
        
        # Bypass SSL verification issues in IronPython older versions
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'pyRevit-RiyanPlugin')
        
        response = urllib2.urlopen(req, context=ctx)
        data = json.loads(response.read())
        remote_commit = data['sha']
        
        # If hashes don't match, we have an update!
        if local_commit != remote_commit:
            show_branded_update_dialog(plugin_dir)
            
    except Exception:
        # If offline or API rate-limited, fail silently so we don't break Revit startup
        pass

def show_branded_update_dialog(plugin_dir):
    xaml_str = """
    <Window
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Update Available"
        Width="450" Height="280"
        WindowStartupLocation="CenterScreen"
        ResizeMode="NoResize"
        FontFamily="Segoe UI"
        Background="Black"
        WindowStyle="ToolWindow">

        <Window.Resources>
            <Style TargetType="Button" x:Key="PrimaryBtn">
                <Setter Property="Background"      Value="#7B2C2C"/>
                <Setter Property="Foreground"      Value="White"/>
                <Setter Property="FontSize"        Value="13"/>
                <Setter Property="FontWeight"      Value="SemiBold"/>
                <Setter Property="BorderThickness" Value="0"/>
                <Setter Property="Padding"         Value="30,8"/>
                <Setter Property="Cursor"          Value="Hand"/>
                <Setter Property="Template">
                    <Setter.Value>
                        <ControlTemplate TargetType="Button">
                            <Border Background="{TemplateBinding Background}"
                                    CornerRadius="5" Padding="{TemplateBinding Padding}">
                                <ContentPresenter HorizontalAlignment="Center"
                                                  VerticalAlignment="Center"/>
                            </Border>
                            <ControlTemplate.Triggers>
                                <Trigger Property="IsMouseOver" Value="True">
                                    <Setter Property="Background" Value="#621F1F"/>
                                </Trigger>
                                <Trigger Property="IsPressed" Value="True">
                                    <Setter Property="Background" Value="#4E1818"/>
                                </Trigger>
                            </ControlTemplate.Triggers>
                        </ControlTemplate>
                    </Setter.Value>
                </Setter>
            </Style>

            <Style TargetType="Button" x:Key="SecondaryBtn">
                <Setter Property="Background"      Value="Black"/>
                <Setter Property="Foreground"      Value="#A0A0A0"/>
                <Setter Property="FontSize"        Value="13"/>
                <Setter Property="BorderThickness" Value="1"/>
                <Setter Property="BorderBrush"     Value="#404040"/>
                <Setter Property="Padding"         Value="20,8"/>
                <Setter Property="Cursor"          Value="Hand"/>
                <Setter Property="Template">
                    <Setter.Value>
                        <ControlTemplate TargetType="Button">
                            <Border Background="{TemplateBinding Background}"
                                    BorderBrush="{TemplateBinding BorderBrush}"
                                    BorderThickness="{TemplateBinding BorderThickness}"
                                    CornerRadius="5" Padding="{TemplateBinding Padding}">
                                <ContentPresenter HorizontalAlignment="Center"
                                                  VerticalAlignment="Center"/>
                            </Border>
                            <ControlTemplate.Triggers>
                                <Trigger Property="IsMouseOver" Value="True">
                                    <Setter Property="Background" Value="#1A1A1A"/>
                                </Trigger>
                            </ControlTemplate.Triggers>
                        </ControlTemplate>
                    </Setter.Value>
                </Setter>
            </Style>
        </Window.Resources>

        <Grid>
            <Grid.RowDefinitions>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="*"/>
            </Grid.RowDefinitions>

            <!-- Header bar -->
            <Border Grid.Row="0" Background="#111111" BorderBrush="#7B2C2C" BorderThickness="0,0,0,2" Padding="20,12">
                <Grid>
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="*"/>
                        <ColumnDefinition Width="Auto"/>
                    </Grid.ColumnDefinitions>
                    <StackPanel Grid.Column="0" VerticalAlignment="Center">
                        <TextBlock Text="Riyan Plugin Update"
                                   FontSize="16" FontWeight="Bold"
                                   Foreground="White"/>
                        <TextBlock Text="New version available"
                                   FontSize="11" Foreground="#A0A0A0" Margin="0,2,0,0"/>
                    </StackPanel>
                    <Image x:Name="LogoImage" Grid.Column="1"
                           Height="40" Width="70"
                           HorizontalAlignment="Right"
                           VerticalAlignment="Center"
                           Margin="16,0,0,0"
                           RenderOptions.BitmapScalingMode="HighQuality"/>
                </Grid>
            </Border>

            <!-- Content area -->
            <StackPanel Grid.Row="1" Margin="24,20,24,20" VerticalAlignment="Center">
                <TextBlock Text="A new update is available for the Revit tools."
                           FontSize="13" Foreground="#E0E0E0" TextWrapping="Wrap" Margin="0,0,0,8"/>
                <TextBlock Text="Would you like to auto-update the plugin to the newest version now?"
                           FontSize="12" Foreground="#A0A0A0" TextWrapping="Wrap" Margin="0,0,0,20"/>
                
                <StackPanel Orientation="Horizontal" HorizontalAlignment="Right">
                    <Button x:Name="LaterBtn" Content="Later" Style="{StaticResource SecondaryBtn}" Margin="0,0,10,0"/>
                    <Button x:Name="UpdateBtn" Content="Update Now" Style="{StaticResource PrimaryBtn}"/>
                </StackPanel>
            </StackPanel>
        </Grid>
    </Window>
    """
    
    # Load Window from XAML
    window = XamlReader.Parse(xaml_str)
    
    # Setup logo image path
    logo_path = os.path.join(plugin_dir, "Riyan.tab", "Link Tools.panel", "Copy from Link.pushbutton", "logo.png")
    
    # Needs to be absolute URI for WPF Image
    logo_img = window.FindName("LogoImage")
    if os.path.exists(logo_path):
        uri = Uri(logo_path, UriKind.Absolute)
        bitmap = BitmapImage(uri)
        logo_img.Source = bitmap
        
    # Wire up button events
    later_btn = window.FindName("LaterBtn")
    update_btn = window.FindName("UpdateBtn")
    
    def on_later_clicked(sender, args):
        window.Close()
        
    def on_update_clicked(sender, args):
        window.Close()
        try:
            # Auto-update via Git
            # Try to find git in system PATH first, fallback to common path
            git_path = "git"
            try:
                # Use shell=True for searching system path on Windows
                subprocess.check_call([git_path, "--version"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except Exception:
                git_path = r"C:\Program Files\Git\cmd\git.exe"
                if not os.path.exists(git_path):
                    forms.alert("Git not found. Please install Git on this PC to use auto-update.", title="Update Failed")
                    return

            process = subprocess.Popen(
                [git_path, "pull", "origin", "main"],
                cwd=plugin_dir,
                shell=True if git_path == "git" else False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                show_branded_success_dialog(plugin_dir)
            else:
                forms.alert("Failed to update. Error: " + str(stderr), title="Update Failed")
        except Exception as e:
            forms.alert(str(e), title="Update Error")

    later_btn.Click += on_later_clicked
    update_btn.Click += on_update_clicked
    
    # Show dialog
    window.ShowDialog()

def show_branded_success_dialog(plugin_dir):
    xaml_str = """
    <Window
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Update Successful"
        Width="450" Height="280"
        WindowStartupLocation="CenterScreen"
        ResizeMode="NoResize"
        FontFamily="Segoe UI"
        Background="Black"
        WindowStyle="ToolWindow">

        <Window.Resources>
            <Style TargetType="Button" x:Key="PrimaryBtn">
                <Setter Property="Background"      Value="#7B2C2C"/>
                <Setter Property="Foreground"      Value="White"/>
                <Setter Property="FontSize"        Value="13"/>
                <Setter Property="FontWeight"      Value="SemiBold"/>
                <Setter Property="BorderThickness" Value="0"/>
                <Setter Property="Padding"         Value="30,8"/>
                <Setter Property="Cursor"          Value="Hand"/>
                <Setter Property="Template">
                    <Setter.Value>
                        <ControlTemplate TargetType="Button">
                            <Border Background="{TemplateBinding Background}"
                                    CornerRadius="5" Padding="{TemplateBinding Padding}">
                                <ContentPresenter HorizontalAlignment="Center"
                                                  VerticalAlignment="Center"/>
                            </Border>
                            <ControlTemplate.Triggers>
                                <Trigger Property="IsMouseOver" Value="True">
                                    <Setter Property="Background" Value="#621F1F"/>
                                </Trigger>
                                <Trigger Property="IsPressed" Value="True">
                                    <Setter Property="Background" Value="#4E1818"/>
                                </Trigger>
                            </ControlTemplate.Triggers>
                        </ControlTemplate>
                    </Setter.Value>
                </Setter>
            </Style>
        </Window.Resources>

        <Grid>
            <Grid.RowDefinitions>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="*"/>
            </Grid.RowDefinitions>

            <!-- Header bar -->
            <Border Grid.Row="0" Background="#111111" BorderBrush="#7B2C2C" BorderThickness="0,0,0,2" Padding="20,12">
                <Grid>
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="*"/>
                        <ColumnDefinition Width="Auto"/>
                    </Grid.ColumnDefinitions>
                    <StackPanel Grid.Column="0" VerticalAlignment="Center">
                        <TextBlock Text="Update Complete"
                                   FontSize="16" FontWeight="Bold"
                                   Foreground="White"/>
                        <TextBlock Text="Riyan Plugin is up to date"
                                   FontSize="11" Foreground="#A0A0A0" Margin="0,2,0,0"/>
                    </StackPanel>
                    <Image x:Name="LogoImage" Grid.Column="1"
                           Height="40" Width="70"
                           HorizontalAlignment="Right"
                           VerticalAlignment="Center"
                           Margin="16,0,0,0"
                           RenderOptions.BitmapScalingMode="HighQuality"/>
                </Grid>
            </Border>

            <!-- Content area -->
            <StackPanel Grid.Row="1" Margin="24,20,24,20" VerticalAlignment="Center">
                <TextBlock Text="The plugin has been updated successfully! 🚀"
                           FontSize="14" FontWeight="SemiBold" Foreground="White" Margin="0,0,0,8"/>
                <TextBlock Text="Please restart Revit to load the new changes and features."
                           FontSize="12" Foreground="#A0A0A0" TextWrapping="Wrap" Margin="0,0,0,20"/>
                
                <Button x:Name="OkBtn" Content="Done" Style="{StaticResource PrimaryBtn}" HorizontalAlignment="Right"/>
            </StackPanel>
        </Grid>
    </Window>
    """
    
    # Load Window from XAML
    window = XamlReader.Parse(xaml_str)
    
    # Setup logo
    logo_path = os.path.join(plugin_dir, "Riyan.tab", "Link Tools.panel", "Copy from Link.pushbutton", "logo.png")
    logo_img = window.FindName("LogoImage")
    if os.path.exists(logo_path):
        logo_img.Source = BitmapImage(Uri(logo_path, UriKind.Absolute))
        
    # Wire up button
    ok_btn = window.FindName("OkBtn")
    def on_ok_clicked(sender, args):
        window.Close()
    ok_btn.Click += on_ok_clicked
    
    window.ShowDialog()

# Run the update check when Revit starts
check_for_updates()
